# Phân Tích Thuật Toán & Mã Nguồn Hệ Thống Gợi Ý (Course Recommendation System)

Tài liệu này phân tích chi tiết về thuật toán, công thức toán học và mã nguồn của từng chức năng cốt lõi trong hệ thống gợi ý khóa học lai (Hybrid Course Recommendation System). Hệ thống được xây dựng trên mô hình Full-stack với:
- **Backend**: Python HTTP Server ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py)).
- **Frontend**: Vite + React ([App.jsx](file:///C:/Users/ADMIN/Desktop/Recomment/client/src/App.jsx)).

---

## 1. Chức Năng Search (Tìm kiếm cơ bản)

### 1.1. Cách Hoạt Động & Cơ Chế Lọc
- Người dùng nhập vào một từ khóa tìm kiếm (Ví dụ: *"Python"*).
- Backend sẽ quét qua danh sách các khóa học được nạp sẵn trong bộ nhớ và tìm kiếm khóa học đầu tiên có tên chứa chuỗi từ khóa mà người dùng nhập vào (không phân biệt chữ hoa, chữ thường).
- Nếu tìm thấy khóa học khớp nhất, hệ thống sẽ sử dụng chỉ số (index) của khóa học đó làm mốc tham chiếu cho thuật toán gợi ý nội dung (Explore).

### 1.2. Mã Nguồn Minh Họa

#### Backend ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L471-L476))
```python
# Quét tìm chỉ số khóa học khớp đầu tiên
match_idx = next(
    (i for i, c in enumerate(courses) if course_name.lower() in c['Course Name'].lower()),
    -1
)
```

#### Frontend ([App.jsx](file:///C:/Users/ADMIN/Desktop/Recomment/client/src/App.jsx#L159-L182))
```javascript
const handleSearch = useCallback(async (query) => {
  if (!query.trim()) return;
  setMode('explore');
  setIsLoading(true);
  setError(null);
  setLastQuery(query);

  try {
    const res = await fetch(`/api/recommend?course_name=${encodeURIComponent(query)}`);
    if (!res.ok) {
      if (res.status === 404) throw new Error("Course not found in our database.");
      throw new Error("Failed to fetch recommendations.");
    }
    const data = await res.json();
    setExploreCourses(data.recommendations || []);
    setHasSearched(true);
  } catch (err) {
    setError(err.message);
    setExploreCourses([]);
  } finally {
    setIsLoading(false);
  }
}, []);
```

---

## 2. Chức Năng Explore (Content-Based Recommendation)

### 2.1. Cách Hoạt Động & Thuật Toán
Tab **Explore** gợi ý các khóa học có nội dung tương đồng nhất với khóa học đích bằng phương pháp **Lọc dựa trên nội dung (Content-Based Filtering)**. Hệ thống chỉ phân tích các thuộc tính văn bản của khóa học mà không quan tâm đến hành vi của người dùng khác.

#### Công thức TF-IDF (Tần suất từ - Tần suất nghịch đảo tài liệu)
Hệ thống sử dụng TF-IDF để lượng hóa nội dung văn bản mô tả của từng khóa học:
1. **IDF (Inverse Document Frequency)**: Đo lường độ quan trọng của từ $w$ trên toàn bộ tập khóa học $D$:
   $$\text{IDF}(w) = \ln\left(\frac{N}{\text{DF}(w) + 1}\right)$$
   *(Trong đó: $N$ là tổng số khóa học, $\text{DF}(w)$ là số khóa học chứa từ $w$.)*
2. **TF-IDF**: Tính độ quan trọng của từ $w$ đối với một khóa học cụ thể $d$:
   $$\text{TF-IDF}(w, d) = \text{TF}(w, d) \times \text{IDF}(w)$$
   *(Trong đó: $\text{TF}(w, d)$ là số lần từ $w$ xuất hiện trong mô tả khóa học $d$.)*
3. **L2 Normalization (Chuẩn hóa Vector)**: Đảm bảo độ dài mỗi vector bằng 1, giúp loại bỏ ảnh hưởng của độ dài văn bản:
   $$\mathbf{v}_{\text{normalized}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \frac{\mathbf{v}}{\sqrt{\sum_{w} (\text{TF-IDF}(w, d))^2}}$$

#### Độ tương đồng Cosine (Cosine Similarity)
Đo góc giữa hai vector TF-IDF đã được chuẩn hóa $\mathbf{a}$ và $\mathbf{b}$ đại diện cho khóa học mục tiêu và khóa học ứng viên:
$$\text{Sim}(\mathbf{a}, \mathbf{b}) = \mathbf{a} \cdot \mathbf{b} = \sum_{w \in \mathbf{a} \cap \mathbf{b}} \mathbf{a}[w] \times \mathbf{b}[w]$$

### 2.2. Mã Nguồn Minh Họa

#### Backend ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L481-L499))
```python
def cosine_similarity(vec1, vec2):
    """Tính tích vô hướng giữa hai vector thưa thớt đã chuẩn hóa."""
    common = set(vec1.keys()) & set(vec2.keys())
    return sum(vec1[w] * vec2[w] for w in common)

# Đo độ tương quan và sắp xếp
target_vector = tfidf_matrix[match_idx]
scored = [
    (i, cosine_similarity(target_vector, vec))
    for i, vec in enumerate(tfidf_matrix)
    if i != match_idx
]
scored = [(i, s) for i, s in scored if s > 0]
scored.sort(key=lambda x: x[1], reverse=True)

# Lấy 6 khóa học tương đồng nhất
recommendations = [build_course_response(i, s, "score") for i, s in scored[:6]]
```

---

## 3. Chức Năng My History (Lịch sử & Persistence)

### 3.1. Cách Hoạt Động & Đồng Bộ CSV
- **My History** là trang hiển thị hồ sơ học tập của bạn.
- Mọi hoạt động đăng ký (`/enroll`) hay đánh giá sao (`/rate`) từ client sẽ lập tức cập nhật vào bộ nhớ đệm RAM (`user_enrollments` và `user_ratings`) của server.
- Để đảm bảo tính bền vững (Persistence) không bị mất khi khởi động lại server, backend ghi nhận và cập nhật ngay vào tệp dữ liệu phẳng [users.csv](file:///C:/Users/ADMIN/Desktop/Recomment/server/users.csv).

### 3.2. Mã Nguồn Minh Họa

#### Backend ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L188-L258))
```python
def save_user_to_csv(user_id):
    """Lưu/Cập nhật lịch sử của một người dùng vào file CSV."""
    global user_enrollments, user_ratings, courses
    enrolled_indices = sorted(list(user_enrollments[user_id]))
    ratings_dict = user_ratings[user_id]
    
    enrolled_str = "|".join(str(idx) for idx in enrolled_indices)
    enrolled_names_str = "|".join(courses[idx].get('Course Name', 'Unknown') for idx in enrolled_indices)
    ratings_str = "|".join(f"{idx}:{rating}" for idx, rating in ratings_dict.items())
    
    rows = []
    updated = False
    fieldnames = ['user_id', 'interests', 'num_enrolled', 'num_rated', 'enrolled_course_indices', 'enrolled_course_names', 'ratings']
    
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if reader.fieldnames:
                fieldnames = reader.fieldnames
                
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
            if key not in new_row: new_row[key] = ''
        rows.append(new_row)
        
    with open(USERS_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
```

---

## 4. Chức Năng Collaborative (Đề xuất cộng tác)

### 4.1. Cách Hoạt Động & Cơ Chế Lọc
Tab **Collaborative** gợi ý các khóa học dựa trên **Lọc cộng tác dựa trên người dùng (User-Based Collaborative Filtering)**:
1. So sánh lịch sử tương tác của người học đích với những người học khác bằng **Hệ số tương quan Pearson (Pearson Correlation Coefficient - PCC)** để lọc ra 10 người có gu học tập tương đồng nhất (top peers).
2. Dự đoán điểm số mà người học đích sẽ chấm cho một khóa học chưa tương tác $c$ dựa trên độ lệch chấm điểm của nhóm peers.
3. Giải quyết vấn đề **Cold Start** bằng cách tự động đề xuất các khóa học phổ biến có rating cao nhất hệ thống nếu tài khoản chưa có lịch sử tương tác.

#### Hệ số tương quan Pearson (Pearson Correlation Coefficient)
Để loại bỏ sự sai lệch thói quen chấm điểm (người dễ tính thường chấm 5 sao, người khó tính thường chỉ chấm 3 sao), công thức PCC đo tương quan giữa người dùng $A$ và $B$:
$$\text{Sim}(A, B) = \frac{\sum_{i \in I_{AB}} (R(A, i) - \bar{R}_A)(R(B, i) - \bar{R}_B)}{\sqrt{\sum_{i \in I_{AB}} (R(A, i) - \bar{R}_A)^2} \sqrt{\sum_{i \in I_{AB}} (R(B, i) - \bar{R}_B)^2}}$$
*Trong đó: $I_{AB}$ là tập khóa học mà cả $A$ và $B$ cùng đánh giá. $\bar{R}_A, \bar{R}_B$ là điểm đánh giá trung bình tương ứng.*

#### Công thức Dự đoán điểm số (Predicted Rating)
Điểm đánh giá dự đoán $\hat{R}(u, c)$ của người dùng $u$ cho khóa học $c$:
$$\hat{R}(u, c) = \bar{R}_u + \frac{\sum_{p \in P_u} \text{Sim}(u, p) \times (R(p, c) - \bar{R}_p)}{\sum_{p \in P_u} \text{Sim}(u, p)}$$
*Trong đó: $P_u$ là tập hợp các người dùng tương đồng (peers).*

### 4.2. Mã Nguồn Minh Họa

#### Backend ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L302-L350))
```python
def collaborative_recommend(user_id, top_n=6):
    target_vec = get_user_vector(user_id)
    if not target_vec:
        return [], "no_history"

    target_mean = sum(target_vec.values()) / len(target_vec)
    similarities = []
    all_users = set(user_ratings.keys()) | set(user_enrollments.keys())
    all_users.discard(user_id)

    # Tìm độ tương đồng hành vi của người học khác
    for other_id in all_users:
        other_vec = get_user_vector(other_id)
        other_mean = sum(other_vec.values()) / len(other_vec)
        sim = user_vector_similarity(target_vec, target_mean, other_vec, other_mean)
        if sim > 0:
            similarities.append((other_id, sim, other_mean))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_peers = similarities[:10]

    # Cộng gộp điểm dự đoán có trọng số
    score_accum = defaultdict(float)
    weight_accum = defaultdict(float)
    for peer_id, sim, peer_mean in top_peers:
        peer_vec = get_user_vector(peer_id)
        for course_idx, rating in peer_vec.items():
            if course_idx in target_vec: continue
            score_accum[course_idx] += sim * (rating - peer_mean)
            weight_accum[course_idx] += sim

    if not score_accum:
        return [], "no_peers"

    # Tính điểm dự đoán
    predicted = {}
    for idx in score_accum:
        pred_val = target_mean + (score_accum[idx] / weight_accum[idx])
        predicted[idx] = max(1.0, min(5.0, pred_val))

    sorted_courses = sorted(predicted.items(), key=lambda x: x[1], reverse=True)
    return sorted_courses[:top_n], "ok"
```

---

## 5. Chức Năng AI Hybrid (Gợi ý lai đa tầng)

### 5.1. Cách Hoạt Động & Thuật Toán
Tab **AI Hybrid** kết hợp cả hai thuật toán trên thông qua mô hình **Weighted Hybrid (Lai ghép trọng số)** để đưa ra kết quả tối ưu:
1. **Thành phần lọc cộng tác (CF)**: Tính toán điểm đánh giá dự đoán của người dùng dựa trên hành vi của các người dùng tương đồng, sau đó chuyển đổi điểm số $[1, 5]$ về khoảng $[0, 1]$:
   $$\text{CF\_Score}(c) = \frac{\hat{R}(u, c) - 1.0}{4.0}$$
2. **Thành phần lọc nội dung (Content)**: Xây dựng một **Vector Hồ sơ người học (User Profile Vector)** $\vec{\mathbf{U}}$ bằng cách lấy trung bình có trọng số từ các vector TF-IDF của các khóa học mà người dùng đích đã học (trọng số chính là điểm đánh giá của họ):
   $$\vec{\mathbf{U}} = \frac{\sum_{i \in I} R_i \cdot \vec{\mathbf{T}}_i}{\sum_{i \in I} R_i}$$
   Sau đó, tính toán độ tương đồng Cosine giữa vector sở thích $\vec{\mathbf{U}}$ này với các khóa học ứng viên chưa học $c$:
   $$\text{Content\_Score}(c) = \text{CosineSimilarity}(\vec{\mathbf{U}}, \vec{\mathbf{T}}_c)$$
3. **Kết hợp kết quả lai**:
   $$\text{Hybrid\_Score}(c) = \alpha \times \text{CF\_Score}(c) + (1 - \alpha) \times \text{Content\_Score}(c)$$
   *Hệ thống thiết lập trọng số cân bằng $\alpha = 0.5$.*

### 5.2. Mã Nguồn Minh Họa

#### Backend ([server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L353-L446))
```python
def hybrid_recommend(user_id, top_n=6, alpha=0.5):
    target_vec = get_user_vector(user_id)
    if not target_vec:
        return [], "no_history"
        
    # --- 1. COLLABORATIVE FILTERING COMPONENT ---
    # (Tìm top_peers và dự đoán điểm cf_predictions cho từng khóa học)
    # Chuẩn hóa cf_predictions về khoảng [0.0, 1.0]
    # cf_predictions[idx] = (pred_val - 1.0) / 4.0

    # --- 2. CONTENT-BASED COMPONENT (USER PROFILE) ---
    user_profile = defaultdict(float)
    total_weight = 0.0
    for idx, rating in target_vec.items():
        if 0 <= idx < len(tfidf_matrix):
            weight = rating
            total_weight += weight
            for word, val in tfidf_matrix[idx].items():
                user_profile[word] += val * weight
                
    if total_weight > 0:
        for word in user_profile:
            user_profile[word] /= total_weight
        norm = math.sqrt(sum(val**2 for val in user_profile.values()))
        if norm > 0:
            user_profile = {k: v / norm for k, v in user_profile.items()}
    else:
        user_profile = {}

    # --- 3. COMBINE BOTH ---
    hybrid_scores = {}
    for idx in range(len(courses)):
        if idx in target_vec: continue
        
        cf_score = cf_predictions.get(idx, 0.0)
        content_score = 0.0
        if user_profile and idx < len(tfidf_matrix):
            content_score = cosine_similarity(user_profile, tfidf_matrix[idx])
            
        # Tổ hợp lai theo trọng số alpha
        hybrid_scores[idx] = alpha * cf_score + (1.0 - alpha) * content_score
        
    if not hybrid_scores:
        return [], "no_recs"
        
    sorted_courses = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_courses[:top_n], "ok"
```
