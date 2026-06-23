# Phân tích chi tiết File Server (`server.py`)

File [server.py](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py) triển khai một hệ thống gợi ý khóa học (Course Recommendation Engine) tích hợp cả hai phương pháp: **Content-Based Filtering** (Gợi ý dựa trên nội dung) và **User-Based Collaborative Filtering** (Lọc cộng tác dựa trên người dùng). Server được phát triển bằng thư viện chuẩn `http.server` của Python, sử dụng dữ liệu tĩnh từ hai tệp CSV: `Coursera.csv` (dữ liệu khóa học) và `users.csv` (dữ liệu người dùng).

---

## 1. Tổng quan về Cách Hoạt Động của Server

Khi bắt đầu khởi chạy (hàm `main`), server thực hiện quy trình chuẩn bị dữ liệu qua các bước sau:
1. **Khởi tạo dữ liệu Content-Based**: Đọc toàn bộ khóa học từ `Coursera.csv`, ghép các trường văn bản quan trọng (Tên khóa học, Độ khó, Kỹ năng, Mô tả), tách từ (tokenize), tính toán chỉ số **TF-IDF** cho từng từ trong từng tài liệu, và xây dựng một **ma trận TF-IDF** được chuẩn hóa độ dài vector (L2 norm).
2. **Khởi tạo dữ liệu Collaborative Filtering**: Đọc thông tin người dùng từ `users.csv`, thiết lập bộ nhớ đệm (cache) trong bộ nhớ RAM lưu trữ:
   - Các khóa học người dùng đã đăng ký (`user_enrollments`).
   - Đánh giá của người dùng với khóa học từ 1.0 đến 5.0 (`user_ratings`).
3. **Mở cổng lắng nghe**: Bắt đầu lắng nghe các kết nối HTTP tại địa chỉ `http://localhost:8000` (hoặc cổng cấu hình trong `.env`).

---

## 2. Chi tiết Chức năng của Các Hàm

Dưới đây là chi tiết chức năng của từng hàm trong mã nguồn:

### Nhóm khởi tạo và cấu hình
* **[load_dotenv](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L16-L25)**:
  * **Chức năng**: Đọc tệp cấu hình `.env` thủ công và lưu các tham số cấu hình vào biến môi trường `os.environ` (ví dụ: `PORT`, `DATA_FILE`, `USERS_FILE`).
* **[safe_float](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L46-L53)**:
  * **Chức năng**: Chuyển đổi an toàn một giá trị bất kỳ sang kiểu số thực (`float`). Nếu xảy ra lỗi chuyển đổi (ví dụ: giá trị chuỗi rỗng hoặc văn bản "Not Calibrated"), hàm sẽ trả về giá trị mặc định là `0.0`.
* **[tokenize](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L60-L63)**:
  * **Chức năng**: Nhận đầu vào là một chuỗi văn bản, chuyển thành chữ thường, sau đó tách thành danh sách các từ và lọc bỏ ký tự đặc biệt, chỉ giữ lại các ký tự chữ cái và chữ số (`isalnum()`).
* **[load_and_prepare_data](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L66-L127)**:
  * **Chức năng**:
    * Đọc dữ liệu khóa học từ tệp `Coursera.csv`.
    * Kết hợp dữ liệu văn bản của mỗi khóa học để tách từ (tokenize).
    * Tính tần suất tài liệu (Document Frequency - DF) để tìm tần suất nghịch đảo (Inverse Document Frequency - IDF) cho từng từ.
    * Tính toán ma trận vector TF-IDF cho toàn bộ khóa học và thực hiện chuẩn hóa L2 (L2 normalization) để mỗi vector có độ dài bằng 1.
* **[load_users_csv](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L128-L187)**:
  * **Chức năng**: Đọc dữ liệu từ `users.csv` để khởi tạo dữ liệu ban đầu cho hệ thống lọc cộng tác.
    * Phân tích chuỗi ghi nhận đăng ký khóa học (phân tách bằng ký tự `|`) lưu vào `user_enrollments`.
    * Phân tích điểm đánh giá của người dùng (dạng `course_idx:rating`, phân tách bằng ký tự `|`) lưu vào `user_ratings`.

### Nhóm tính toán gợi ý (Recommendation Engine)
* **[cosine_similarity](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L188-L191)**:
  * **Chức năng**: Tính toán độ tương đồng cosine (Cosine Similarity) giữa hai vector TF-IDF biểu diễn bằng cấu trúc dữ liệu từ điển (`dict`) thưa thớt (sparse representation) cho phần gợi ý Content-Based.
* **[get_user_vector](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L198-L208)**:
  * **Chức năng**: Xây dựng vector sở thích của một người dùng dưới dạng từ điển `{course_idx: rating}`. Nếu người dùng chỉ đăng ký khóa học mà chưa đánh giá điểm số rõ ràng, điểm số ngầm định (implicit rating) sẽ được thiết lập là `3.0`. Nếu có điểm đánh giá cụ thể (explicit rating), nó sẽ ghi đè lên giá trị mặc định.
* **[user_vector_similarity](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L211-L223)**:
  * **Chức năng**: Tính toán **Hệ số tương quan Pearson** (Pearson Correlation Coefficient - PCC) giữa hai vector đánh giá của hai người dùng khác nhau trên các khóa học chung để đo mức độ tương đồng hành vi học tập.
* **[collaborative_recommend](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L226-L270)**:
  * **Chức năng**: Thực hiện thuật toán Lọc cộng tác dựa trên người dùng (User-Based Collaborative Filtering) nâng cấp:
    * Lấy vector đánh giá của người dùng đích và tính điểm đánh giá trung bình (`target_mean`).
    * Tính độ tương đồng Pearson giữa người dùng đích với tất cả những người dùng khác và lưu lại điểm trung bình của họ.
    * Chọn ra nhóm 10 người dùng tương đồng nhất (top peers).
    * Dự đoán điểm đánh giá đối với các khóa học chưa học bằng phương pháp trung bình có trọng số của các điểm số đã chuẩn hóa (trừ đi điểm trung bình của peer), sau đó cộng thêm điểm trung bình của người dùng mục tiêu.
    * Sắp xếp và trả về danh sách các khóa học được dự đoán điểm cao nhất.
* **[build_course_response](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L273-L285)**:
  * **Chức năng**: Chuyển đổi chỉ mục khóa học (`idx`) và điểm số gợi ý (`score`) thành một đối tượng từ điển chi tiết chứa đầy đủ thông tin khóa học để sẵn sàng trả về cho phía client.

### Nhóm API Server (`RequestHandler`)
* **[RequestHandler](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L292-L513)**:
  * Lớp xử lý yêu cầu HTTP. Định nghĩa các API Endpoints và điều phối luồng dữ liệu:
    * **[do_OPTIONS](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L302-L304)**: Xử lý cơ chế tiền kiểm CORS (Preflight Request).
    * **[do_POST](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L308-L361)**: Phân tuyến các yêu cầu POST gồm `/enroll` và `/rate`.
    * **[do_GET](file:///C:/Users/ADMIN/Desktop/Recomment/server/server.py#L365-L383)**: Phân tuyến các yêu cầu GET gồm `/recommend`, `/recommend/user` và `/profile`.

---

## 3. Các Hàm Có Tính Toán Chi Tiết và Công Thức Sử Dụng

Có 4 hàm thực hiện các công thức toán học và thống kê phức tạp để xây dựng thuật toán gợi ý:

### 3.1. Phép toán trong `load_and_prepare_data`
Hàm này thực hiện tính toán giá trị **TF-IDF** cho từng từ $w$ trong từng khóa học (tài liệu) $d$ thuộc tập hợp tài liệu $D$:
1. **Tính IDF (Tần suất tài liệu nghịch đảo)**:
   $$\text{IDF}(w) = \ln\left(\frac{N}{\text{DF}(w) + 1}\right)$$
   *Trong đó: $N$ là tổng số khóa học (`num_docs`), $\text{DF}(w)$ là số lượng khóa học chứa từ $w$ (`count`).*
2. **Tính TF-IDF thô**:
   $$\text{TF-IDF}(w, d) = \text{TF}(w, d) \times \text{IDF}(w)$$
   *Trong đó: $\text{TF}(w, d)$ là tần suất xuất hiện của từ $w$ trong tài liệu $d$.*
3. **Chuẩn hóa vector L2 (L2 Normalization)**:
   $$\mathbf{v}_{\text{normalized}} = \frac{\mathbf{v}}{\|\mathbf{v}\|_2} = \frac{\mathbf{v}}{\sqrt{\sum_{w} (\text{TF-IDF}(w, d))^2}}$$

### 3.2. Hàm `cosine_similarity`
Tính toán độ tương đồng Cosine giữa hai vector TF-IDF đã được chuẩn hóa đơn vị $\mathbf{a}$ và $\mathbf{b}$ đại diện cho nội dung của hai khóa học:
$$\text{Sim}(\mathbf{a}, \mathbf{b}) = \mathbf{a} \cdot \mathbf{b} = \sum_{w \in \mathbf{a} \cap \mathbf{b}} \mathbf{a}[w] \times \mathbf{b}[w]$$

### 3.3. Hàm `user_vector_similarity` (Nâng cấp)
Tính độ tương đồng Pearson (Pearson Correlation Coefficient - PCC) giữa hai người dùng $A$ (vector $\mathbf{u}_A$ có điểm trung bình $\bar{R}_A$) và $B$ (vector $\mathbf{u}_B$ có điểm trung bình $\bar{R}_B$):
$$\text{Sim}(A, B) = \frac{\sum_{i \in I_{AB}} (R(A, i) - \bar{R}_A)(R(B, i) - \bar{R}_B)}{\sqrt{\sum_{i \in I_{AB}} (R(A, i) - \bar{R}_A)^2} \sqrt{\sum_{i \in I_{AB}} (R(B, i) - \bar{R}_B)^2}}$$
*Trong đó: $I_{AB}$ là tập hợp các khóa học chung mà cả hai người dùng cùng tương tác. Công thức này giúp chuẩn hóa thói quen đánh giá của từng người dùng bằng cách trừ đi điểm trung bình của họ.*

### 3.4. Hàm `collaborative_recommend` (Nâng cấp)
Tính toán dự đoán điểm đánh giá (Predicted Rating) cho một khóa học chưa tương tác $c$ của người dùng đích $u$ bằng cách điều chỉnh theo điểm đánh giá trung bình $\bar{R}_u$:
$$\hat{R}(u, c) = \bar{R}_u + \frac{\sum_{p \in P_u} \text{Sim}(u, p) \times (R(p, c) - \bar{R}_p)}{\sum_{p \in P_u} \text{Sim}(u, p)}$$
*Trong đó: $P_u$ là tập hợp 10 hàng xóm có độ tương đồng Pearson dương lớn nhất với người dùng $u$, và $R(p, c)$ là điểm đánh giá của người dùng tương đồng $p$ cho khóa học $c$.*

---

## 4. Ảnh Hưởng của Các Hàm Đến Kết Quả Gợi Ý (Recommendation)

| Tên Hàm | Ảnh hưởng trực tiếp đến kết quả gợi ý | Mức độ ảnh hưởng |
| :--- | :--- | :--- |
| **`load_and_prepare_data`** | Xây dựng đặc trưng từ vựng để tính độ tương đồng văn bản giữa các khóa học. | **Rất cao** |
| **`cosine_similarity`** | Đo lường mức độ tương đồng giữa hai khóa học. Quyết định trực tiếp kết quả gợi ý Content-Based. | **Cao** |
| **`get_user_vector`** | Biểu diễn hồ sơ tương tác của học viên (bao gồm điểm số thực tế và điểm số ngầm định 3.0). | **Trung bình** |
| **`user_vector_similarity`** | Đo lường mức độ tương đồng hành vi giữa hai học viên. PCC giúp lọc các người dùng có chung gu học tập chuẩn xác hơn mà không bị ảnh hưởng bởi độ khó/dễ khi chấm điểm. | **Rất cao** |
| **`collaborative_recommend`** | Trung tâm của thuật toán Lọc cộng tác. Thuật toán mới tính toán độ lệch chấm điểm của peers để dự đoán điểm cá nhân hóa chính xác hơn cho người học, sau đó chọn ra top khóa học tốt nhất. | **Rất cao** |
| **`_handle_user_recommend`** | Điều hướng khi người dùng mới gặp hiện tượng Cold Start (sử dụng danh sách các khóa học phổ biến nhất có lượt đánh giá cao nhất làm dự phòng). | **Cao** |
