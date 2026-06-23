import http.server
import json
import csv
import math
import time
import urllib.parse
import sys
import os
from collections import Counter, defaultdict

# Fix Windows terminal encoding for emoji
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# --- LOAD ENVIRONMENT VARIABLES ---
def load_dotenv(dotenv_path=".env"):
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_dotenv()

# --- CONFIGURATION ---
PORT       = int(os.environ.get("PORT", 8000))
DATA_FILE  = os.environ.get("DATA_FILE", "Coursera.csv")
USERS_FILE = os.environ.get("USERS_FILE", "users.csv")

# --- GLOBAL DATA ---
courses = []
tfidf_matrix = []
idf_scores = {}

# --- USER-BASED COLLABORATIVE FILTERING STORE ---
# { user_id: { course_idx: rating (float 1-5) } }
user_ratings = defaultdict(dict)
# { user_id: set of enrolled course indices }
user_enrollments = defaultdict(set)


def safe_float(val, default=0.0):
    """Safely convert value to float, defaulting if it fails (e.g., 'Not Calibrated')."""
    try:
        if val is None:
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


# ──────────────────────────────────────────────
#  CONTENT-BASED ENGINE  (unchanged logic)
# ──────────────────────────────────────────────

def tokenize(text):
    if not text:
        return []
    return [w for w in text.lower().split() if w.isalnum()]


def load_and_prepare_data():
    global courses, tfidf_matrix, idf_scores
    print(f"\n{'='*50}")
    print("🚀 [START] Đang khởi động AI Recommendation Engine...")
    print(f"{'='*50}")

    start_load = time.time()
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            courses = list(reader)

        print(f"📂 [STEP 1] Đã tải {len(courses)} khóa học từ {DATA_FILE}")

        df_counts = Counter()
        doc_tokens = []

        print("🧠 [STEP 2] Đang phân tích nội dung (Tokenizing)...")
        for course in courses:
            tags = " ".join([
                course.get('Course Name', ''),
                course.get('Difficulty Level', ''),
                course.get('Skills', ''),
                course.get('Course Description', '')
            ])
            tokens = tokenize(tags)
            doc_tokens.append(tokens)

            for token in set(tokens):
                df_counts[token] += 1

        num_docs = len(courses)
        idf_scores = {
            word: math.log(num_docs / (count + 1))
            for word, count in df_counts.items()
        }

        print("📊 [STEP 3] Đang tính toán ma trận TF-IDF...")
        for tokens in doc_tokens:
            tf = Counter(tokens)
            doc_tfidf = {}
            for word, count in tf.items():
                tfidf = count * idf_scores.get(word, 0)
                if tfidf > 0:
                    doc_tfidf[word] = tfidf

            norm = math.sqrt(sum(val**2 for val in doc_tfidf.values()))
            if norm > 0:
                doc_tfidf = {k: v / norm for k, v in doc_tfidf.items()}

            tfidf_matrix.append(doc_tfidf)

        process_time = (time.time() - start_load) * 1000
        print(f"✅ [SUCCESS] Search Engine đã sẵn sàng! ({process_time:.2f}ms)")
        print(f"{'='*50}\n")

    except FileNotFoundError:
        print(f"❌ [ERROR] Không tìm thấy file {DATA_FILE}.")
    except Exception as e:
        print(f"❌ [ERROR] {e}")


def load_users_csv():
    """Pre-load users.csv into user_ratings / user_enrollments so the
    collaborative filter has data from the first request."""
    global user_ratings, user_enrollments
    try:
        with open(USERS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        loaded_users = 0
        loaded_enrollments = 0
        loaded_ratings = 0

        for row in rows:
            uid = row.get('user_id', '').strip()
            if not uid:
                continue

            if uid not in user_enrollments:
                user_enrollments[uid] = set()
            if uid not in user_ratings:
                user_ratings[uid] = {}

            # enrolled_course_indices: "0|5|10|..."
            raw_idx = row.get('enrolled_course_indices', '')
            if raw_idx:
                for part in raw_idx.split('|'):
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part)
                        if 0 <= idx < len(courses):
                            user_enrollments[uid].add(idx)
                            loaded_enrollments += 1

            # ratings: "idx:rating|idx:rating|..."
            raw_ratings = row.get('ratings', '')
            if raw_ratings:
                for pair in raw_ratings.split('|'):
                    pair = pair.strip()
                    if ':' in pair:
                        parts = pair.split(':', 1)
                        if parts[0].isdigit():
                            idx = int(parts[0])
                            try:
                                rating = float(parts[1])
                                if 0 <= idx < len(courses) and 1.0 <= rating <= 5.0:
                                    user_ratings[uid][idx] = rating
                                    loaded_ratings += 1
                            except ValueError:
                                pass

            loaded_users += 1

        print(f"👥 [STEP 4] Loaded {loaded_users} users from {USERS_FILE} "
              f"({loaded_enrollments} enrollments, {loaded_ratings} ratings)")
        print(f"{'='*50}\n")

    except FileNotFoundError:
        print(f"⚠️  [WARN] {USERS_FILE} not found — starting with empty user store.")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"❌ [ERROR] Failed loading {USERS_FILE}: {e}")
        print(f"{'='*50}\n")


def save_user_to_csv(user_id):
    """Save/update a single user's history in the CSV file."""
    global user_enrollments, user_ratings, courses
    
    # Get current data for this user
    enrolled_indices = sorted(list(user_enrollments[user_id]))
    ratings_dict = user_ratings[user_id]
    
    enrolled_str = "|".join(str(idx) for idx in enrolled_indices)
    
    enrolled_names = []
    for idx in enrolled_indices:
        if 0 <= idx < len(courses):
            enrolled_names.append(courses[idx].get('Course Name', 'Unknown'))
    enrolled_names_str = "|".join(enrolled_names)
    
    ratings_str = "|".join(f"{idx}:{rating}" for idx, rating in ratings_dict.items())
    
    # Read existing rows
    rows = []
    updated = False
    fieldnames = ['user_id', 'interests', 'num_enrolled', 'num_rated', 'enrolled_course_indices', 'enrolled_course_names', 'ratings']
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if reader.fieldnames:
                    fieldnames = reader.fieldnames
        except Exception as e:
            print(f"⚠️ Error reading {USERS_FILE} during save: {e}")
            
    # Update or append
    for row in rows:
        if row.get('user_id', '').strip() == user_id:
            row['num_enrolled'] = str(len(enrolled_indices))
            row['num_rated'] = str(len(ratings_dict))
            row['enrolled_course_indices'] = enrolled_str
            row['enrolled_course_names'] = enrolled_names_str
            row['ratings'] = ratings_str
            updated = True
            break
            
    if not updated:
        # Create a new row
        new_row = {
            'user_id': user_id,
            'interests': '',
            'num_enrolled': str(len(enrolled_indices)),
            'num_rated': str(len(ratings_dict)),
            'enrolled_course_indices': enrolled_str,
            'enrolled_course_names': enrolled_names_str,
            'ratings': ratings_str
        }
        for key in fieldnames:
            if key not in new_row:
                new_row[key] = ''
        rows.append(new_row)
        
    # Write back to CSV
    try:
        with open(USERS_FILE, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"💾 [SAVE] Saved user history for '{user_id}' to {USERS_FILE}")
    except Exception as e:
        print(f"❌ [SAVE ERROR] Failed to save user history to {USERS_FILE}: {e}")


def cosine_similarity(vec1, vec2):
    """Cosine similarity between two sparse TF-IDF vectors."""
    common = set(vec1.keys()) & set(vec2.keys())
    return sum(vec1[w] * vec2[w] for w in common)


# ──────────────────────────────────────────────
#  USER-BASED COLLABORATIVE FILTERING ENGINE
# ──────────────────────────────────────────────

def get_user_vector(user_id):
    """Return a sparse rating vector {course_idx: rating} for a user.
    Enrollments without explicit rating count as an implicit 3.0."""
    vec = {}
    # Implicit enrollments
    for idx in user_enrollments[user_id]:
        vec[idx] = 3.0
    # Explicit ratings override
    for idx, rating in user_ratings[user_id].items():
        vec[idx] = float(rating)
    return vec


def user_vector_similarity(vec_a, mean_a, vec_b, mean_b):
    """Pearson correlation coefficient between two user rating vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    
    numerator = sum((vec_a[k] - mean_a) * (vec_b[k] - mean_b) for k in common)
    var_a = sum((vec_a[k] - mean_a)**2 for k in common)
    var_b = sum((vec_b[k] - mean_b)**2 for k in common)
    
    if var_a == 0 or var_b == 0:
        return 0.0
    return numerator / math.sqrt(var_a * var_b)


def collaborative_recommend(user_id, top_n=6):
    """User-based CF: find similar users → aggregate their highly-rated courses using PCC."""
    target_vec = get_user_vector(user_id)

    if not target_vec:
        return [], "no_history"   # cold start

    target_mean = sum(target_vec.values()) / len(target_vec)

    # Compute similarity to every other user
    similarities = []
    all_users = set(user_ratings.keys()) | set(user_enrollments.keys())
    all_users.discard(user_id)

    for other_id in all_users:
        other_vec = get_user_vector(other_id)
        other_mean = sum(other_vec.values()) / len(other_vec)
        sim = user_vector_similarity(target_vec, target_mean, other_vec, other_mean)
        if sim > 0:
            similarities.append((other_id, sim, other_mean))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_peers = similarities[:10]   # use top 10 similar users

    # Aggregate scores for unseen courses
    score_accum = defaultdict(float)
    weight_accum = defaultdict(float)

    for peer_id, sim, peer_mean in top_peers:
        peer_vec = get_user_vector(peer_id)
        for course_idx, rating in peer_vec.items():
            if course_idx in target_vec:
                continue   # user already knows this course
            # Normalize by subtracting peer mean
            score_accum[course_idx] += sim * (rating - peer_mean)
            weight_accum[course_idx] += sim

    if not score_accum:
        return [], "no_peers"

    # Predicted rating = target_mean + (weighted average of normalized ratings)
    predicted = {}
    for idx in score_accum:
        pred_val = target_mean + (score_accum[idx] / weight_accum[idx])
        # Clip to [1.0, 5.0]
        predicted[idx] = max(1.0, min(5.0, pred_val))

    sorted_courses = sorted(predicted.items(), key=lambda x: x[1], reverse=True)
    return sorted_courses[:top_n], "ok"


def hybrid_recommend(user_id, top_n=6, alpha=0.5):
    """Hybrid recommendation combining User-Based CF and Content-Based Filtering.
    Score = alpha * normalized_CF_rating + (1 - alpha) * Content_similarity
    """
    global user_ratings, user_enrollments, courses, tfidf_matrix
    
    target_vec = get_user_vector(user_id)
    if not target_vec:
        return [], "no_history"
        
    # --- 1. COLLABORATIVE FILTERING COMPONENT ---
    target_mean = sum(target_vec.values()) / len(target_vec)
    
    similarities = []
    all_users = set(user_ratings.keys()) | set(user_enrollments.keys())
    all_users.discard(user_id)
    
    for other_id in all_users:
        other_vec = get_user_vector(other_id)
        other_mean = sum(other_vec.values()) / len(other_vec)
        sim = user_vector_similarity(target_vec, target_mean, other_vec, other_mean)
        if sim > 0:
            similarities.append((other_id, sim, other_mean))
            
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_peers = similarities[:10]
    
    cf_predictions = {}
    if top_peers:
        score_accum = defaultdict(float)
        weight_accum = defaultdict(float)
        
        for peer_id, sim, peer_mean in top_peers:
            peer_vec = get_user_vector(peer_id)
            for course_idx, rating in peer_vec.items():
                if course_idx in target_vec:
                    continue
                score_accum[course_idx] += sim * (rating - peer_mean)
                weight_accum[course_idx] += sim
                
        for idx in score_accum:
            pred_val = target_mean + (score_accum[idx] / weight_accum[idx])
            pred_val = max(1.0, min(5.0, pred_val))
            # Normalize to 0.0 - 1.0 range
            cf_predictions[idx] = (pred_val - 1.0) / 4.0

    # --- 2. CONTENT-BASED COMPONENT ---
    # Build user profile vector by averaging the TF-IDF vectors of their history, weighted by rating
    user_profile = defaultdict(float)
    total_weight = 0.0
    for idx, rating in target_vec.items():
        if 0 <= idx < len(tfidf_matrix):
            # Higher ratings give more weight to the course vector
            weight = rating
            total_weight += weight
            for word, val in tfidf_matrix[idx].items():
                user_profile[word] += val * weight
                
    if total_weight > 0:
        for word in user_profile:
            user_profile[word] /= total_weight
            
        # Normalize the profile vector
        norm = math.sqrt(sum(val**2 for val in user_profile.values()))
        if norm > 0:
            user_profile = {k: v / norm for k, v in user_profile.items()}
    else:
        user_profile = {}

    # --- 3. COMBINE BOTH ---
    hybrid_scores = {}
    
    # Calculate for all unseen courses
    for idx in range(len(courses)):
        if idx in target_vec:
            continue
            
        # CF score
        cf_score = cf_predictions.get(idx, 0.0) # default to 0 if not predicted by peers
        
        # Content score
        content_score = 0.0
        if user_profile and idx < len(tfidf_matrix):
            content_score = cosine_similarity(user_profile, tfidf_matrix[idx])
            
        # Hybrid combination
        hybrid_scores[idx] = alpha * cf_score + (1.0 - alpha) * content_score
        
    if not hybrid_scores:
        return [], "no_recs"
        
    sorted_courses = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_courses[:top_n], "ok"


def build_course_response(idx, score, score_label="score"):
    row = courses[idx]
    return {
        "name": row.get('Course Name', 'Unknown'),
        "university": row.get('University', 'Unknown'),
        "level": row.get('Difficulty Level', 'Unknown'),
        "rating": row.get('Course Rating', '0.0'),
        "description": row.get('Course Description', ''),
        "url": row.get('Course URL', '#'),
        "skills": row.get('Skills', ''),
        score_label: round(float(score), 4),
        "course_idx": idx
    }


# ──────────────────────────────────────────────
#  HTTP REQUEST HANDLER
# ──────────────────────────────────────────────

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return   # silence default logs

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # ── POST routes ───────────────────────────

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = {}
        if length:
            try:
                body = json.loads(self.rfile.read(length).decode('utf-8'))
            except Exception:
                self.send_error_response(400, "Invalid JSON body")
                return

        # POST /enroll  { user_id, course_idx }
        if parsed_url.path == "/enroll":
            user_id = body.get("user_id", "").strip()
            course_idx = body.get("course_idx")

            if not user_id or course_idx is None:
                self.send_error_response(400, "Missing user_id or course_idx")
                return
            if not (0 <= int(course_idx) < len(courses)):
                self.send_error_response(400, "Invalid course_idx")
                return

            user_enrollments[user_id].add(int(course_idx))
            save_user_to_csv(user_id)
            print(f"📌 [ENROLL] user='{user_id}' course_idx={course_idx}")
            self.send_json_response(200, {"status": "enrolled", "user_id": user_id, "course_idx": course_idx})

        # POST /rate  { user_id, course_idx, rating }
        elif parsed_url.path == "/rate":
            user_id = body.get("user_id", "").strip()
            course_idx = body.get("course_idx")
            rating = body.get("rating")

            if not user_id or course_idx is None or rating is None:
                self.send_error_response(400, "Missing user_id, course_idx, or rating")
                return
            try:
                rating = float(rating)
                if not (1.0 <= rating <= 5.0):
                    raise ValueError()
            except ValueError:
                self.send_error_response(400, "Rating must be 1–5")
                return
            if not (0 <= int(course_idx) < len(courses)):
                self.send_error_response(400, "Invalid course_idx")
                return

            user_ratings[user_id][int(course_idx)] = rating
            user_enrollments[user_id].add(int(course_idx))   # auto-enroll
            save_user_to_csv(user_id)
            print(f"⭐ [RATE] user='{user_id}' course_idx={course_idx} rating={rating}")
            self.send_json_response(200, {"status": "rated", "user_id": user_id, "course_idx": course_idx, "rating": rating})

        else:
            self.send_error_response(404, "Not Found")

    # ── GET routes ────────────────────────────

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        print(f"📥 [GET] Path: {parsed_url.path} | Query Params: {query_params}")
    
        # GET /recommend?course_name=X  (content-based, existing)
        if parsed_url.path == "/recommend":
            self._handle_content_recommend(query_params)

        # GET /recommend/user?user_id=X  (user-based CF, new)
        elif parsed_url.path == "/recommend/user":
            self._handle_user_recommend(query_params)

        # GET /recommend/hybrid?user_id=X (hybrid content + CF)
        elif parsed_url.path == "/recommend/hybrid":
            self._handle_hybrid_recommend(query_params)

        # GET /profile?user_id=X  — returns enrolled + rated courses
        elif parsed_url.path == "/profile":
            self._handle_profile(query_params)

        else:
            self.send_error_response(404, "Not Found")

    def _handle_content_recommend(self, query_params):
        start_time = time.time()
        course_name = query_params.get('course_name', [None])[0]

        if not course_name:
            self.send_error_response(400, "Missing course_name")
            return

        print(f"🔍 [CONTENT] Searching: '{course_name}'")

        match_idx = next(
            (i for i, c in enumerate(courses) if course_name.lower() in c['Course Name'].lower()),
            -1
        )

        if match_idx == -1:
            self.send_error_response(404, "Course not found")
            return

        target_vector = tfidf_matrix[match_idx]
        scored = [
            (i, cosine_similarity(target_vector, vec))
            for i, vec in enumerate(tfidf_matrix)
            if i != match_idx
        ]
        scored = [(i, s) for i, s in scored if s > 0]
        scored.sort(key=lambda x: x[1], reverse=True)

        recommendations = [build_course_response(i, s, "score") for i, s in scored[:6]]

        self.send_json_response(200, {
            "mode": "content_based",
            "course_query": course_name,
            "recommendations": recommendations
        })
        ms = (time.time() - start_time) * 1000
        print(f"✨ [CONTENT] Sent {len(recommendations)} results ({ms:.1f}ms)")

    def _handle_user_recommend(self, query_params):
        start_time = time.time()
        user_id = query_params.get('user_id', [None])[0]

        if not user_id:
            self.send_error_response(400, "Missing user_id")
            return

        user_id = user_id.strip()
        print(f"👤 [USER-CF] Recommending for user='{user_id}'")

        results, status = collaborative_recommend(user_id)

        if status == "no_history" or status == "no_peers":
            sorted_by_rating = sorted(
                range(len(courses)),
                key=lambda i: safe_float(courses[i].get('Course Rating')),
                reverse=True
            )
            recs = [build_course_response(i, safe_float(courses[i].get('Course Rating')), "predicted_rating") for i in sorted_by_rating[:6]]
            self.send_json_response(200, {
                "mode": "user_based",
                "user_id": user_id,
                "status": "cold_start" if status == "no_history" else "popular_fallback",
                "message": "No history yet. Showing popular courses!" if status == "no_history" else "Not enough peers found. Showing popular courses!",
                "recommendations": recs
            })
            return

        recs = [build_course_response(i, s, "predicted_rating") for i, s in results]
        self.send_json_response(200, {
            "mode": "user_based",
            "user_id": user_id,
            "status": "ok",
            "recommendations": recs
        })
        ms = (time.time() - start_time) * 1000
        print(f"✨ [USER-CF] Sent {len(recs)} results for '{user_id}' ({ms:.1f}ms)")

    def _handle_hybrid_recommend(self, query_params):
        start_time = time.time()
        user_id = query_params.get('user_id', [None])[0]

        if not user_id:
            self.send_error_response(400, "Missing user_id")
            return

        user_id = user_id.strip()
        print(f"🧬 [HYBRID] Recommending for user='{user_id}'")

        results, status = hybrid_recommend(user_id)

        if status == "no_history" or status == "no_recs":
            sorted_by_rating = sorted(
                range(len(courses)),
                key=lambda i: safe_float(courses[i].get('Course Rating')),
                reverse=True
            )
            recs = [build_course_response(i, safe_float(courses[i].get('Course Rating')) / 5.0, "score") for i in sorted_by_rating[:6]]
            self.send_json_response(200, {
                "mode": "hybrid",
                "user_id": user_id,
                "status": "cold_start" if status == "no_history" else "popular_fallback",
                "message": "No history yet. Showing popular courses!" if status == "no_history" else "Showing popular courses.",
                "recommendations": recs
            })
            return

        recs = [build_course_response(i, s, "score") for i, s in results]
        self.send_json_response(200, {
            "mode": "hybrid",
            "user_id": user_id,
            "status": "ok",
            "recommendations": recs
        })
        ms = (time.time() - start_time) * 1000
        print(f"✨ [HYBRID] Sent {len(recs)} results for '{user_id}' ({ms:.1f}ms)")

    def _handle_profile(self, query_params):
        user_id = query_params.get('user_id', [None])[0]
        if not user_id:
            self.send_error_response(400, "Missing user_id")
            return

        user_id = user_id.strip()
        is_new_user = user_id not in user_enrollments and user_id not in user_ratings
        if is_new_user:
            user_enrollments[user_id] = set()
            user_ratings[user_id] = {}
            save_user_to_csv(user_id)

        enrolled = list(user_enrollments[user_id])
        rated = user_ratings[user_id]

        history = []
        for idx in enrolled:
            row = courses[idx]
            history.append({
                "course_idx": idx,
                "name": row.get('Course Name', 'Unknown'),
                "university": row.get('University', 'Unknown'),
                "level": row.get('Difficulty Level', 'Unknown'),
                "rating": row.get('Course Rating', '0.0'),
                "url": row.get('Course URL', '#'),
                "description": row.get('Course Description', ''),
                "skills": row.get('Skills', ''),
                "user_rating": rated.get(idx, None)
            })

        self.send_json_response(200, {
            "user_id": user_id,
            "total_enrolled": len(enrolled),
            "total_rated": len(rated),
            "history": history
        })

    # ── Helpers ───────────────────────────────

    def send_json_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_error_response(self, status, detail):
        self.send_json_response(status, {"detail": detail})


# --- RUN ---
if __name__ == "__main__":
    load_and_prepare_data()   # step 1-3: load Coursera.csv + build TF-IDF
    load_users_csv()          # step 4  : pre-load users.csv into CF store
    print(f"🛰️  Recommendation Engine active at http://localhost:{PORT}")
    print("   Content-based : GET  /recommend?course_name=<name>")
    print("   User CF       : GET  /recommend/user?user_id=<id>")
    print("   Enroll        : POST /enroll  {user_id, course_idx}")
    print("   Rate          : POST /rate    {user_id, course_idx, rating}")
    print("   Profile       : GET  /profile?user_id=<id>")
    server = http.server.HTTPServer(("0.0.0.0", PORT), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server đã dừng.")
        server.server_close()