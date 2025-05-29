ACHIEVO INFORMATION (PYTHON STACK VERSION)
==========================================

1\. TRIẾT LÝ PHÁT TRIỂN & QUY TRÌNH
-----------------------------------

### 1.1. Triết lý phát triển

*   **End-to-end Python:**Toàn bộ hệ thống – backend, frontend và smart contract – đều phát triển bằng Python. Điều này đảm bảo tính đồng nhất, dễ maintain, thuận lợi onboarding đội ngũ Pythonist, tối ưu chi phí vận hành và phát triển.
    
*   **KISS, Clean Code:**Code rõ ràng, ưu tiên đơn giản hóa logic, dễ đọc, dễ test. Không phụ thuộc các framework frontend phức tạp hoặc CSS utility như TailwindCSS.
    
*   **Functional, Typed:**Tận dụng typing Python, chia nhỏ logic nghiệp vụ thành hàm thuần, tăng kiểm soát, giảm bug, dễ unit test và tích hợp.
    
*   **SSR-first:**Giao diện sử dụng Jinja2 (Server Side Rendering), không triển khai SPA. Điều này tối ưu SEO, bảo mật và giúp kiểm soát luồng UI dễ dàng, thích hợp với các dashboard quản trị, hệ thống chứng chỉ, tra cứu công khai.
    
*   **Testable, CI/CD:**Code phải chạy được, pass test (pytest), CI/CD tự động hóa build/test/deploy, không merge placeholder hoặc TODO vào nhánh chính. Test coverage cao, pipeline tự động hóa.
    
*   **Bảo mật & Trải nghiệm:**Kiểm tra input nghiêm ngặt, xác thực chặt chẽ (JWT, session), log toàn bộ thao tác quan trọng, rate limit toàn bộ endpoint, UI mobile-friendly, hỗ trợ accessibility cơ bản.
    
*   **Minh bạch:**Tất cả action nghiệp vụ đều log append-only (Firestore), admin có thể kiểm toán, truy xuất lịch sử và xuất log.
    

### 1.2. Quy trình phát triển

*   **Phân tích yêu cầu & User Story:**Viết user story, xác định rõ acceptance criteria cho từng chức năng. Model hóa đầy đủ flow nghiệp vụ (giữa user, tổ chức, admin, blockchain).
    
*   **Thiết kế kiến trúc:**Vẽ sơ đồ hệ thống tổng thể, chi tiết các luồng dữ liệu giữa backend, blockchain, frontend, lưu trữ. Thiết kế API spec chi tiết (REST/OpenAPI).
    
*   **Phát triển:**
    
    *   Viết smart contract OpShin (Python), kiểm thử & build ra Plutus Core.
        
    *   Xây dựng backend Flask: tổ chức rõ ràng module (user, auth, certificate, marketplace...), quản lý session/JWT, các middleware bảo mật, rate limiting, logging.
        
    *   Thiết kế giao diện với Jinja2 template, chia nhỏ thành các view (dashboard, profile, admin, tra cứu, marketplace, v.v.).
        
*   **Testing:**
    
    *   Dùng pytest cho backend, kiểm thử contract OpShin qua toolchain CLI.
        
    *   Manual test UI/logic, có thể bổ sung automated UI test với Selenium hoặc Playwright (Python).
        
*   **CI/CD:**
    
    *   Github Actions (hoặc tương đương): tự động hóa lint, test, build, deploy Flask app lên server (Render.com).
        
*   **Monitoring:**
    
    *   Theo dõi log nghiệp vụ và lỗi (Loguru, Sentry...), alert khi có sự cố, dashboard trạng thái hệ thống nếu cần.
        

### 1.3. Công cụ & Thực hành

*   **Version Control:** Git, Conventional Commits, quản lý issue/milestone (GitHub Projects, ZenHub, v.v.).
    
*   **Code Quality:** Black (format), Flake8 (lint), isort (import order), mypy (type checking), pre-commit hook.
    
*   **Dependency Management:** pip, requirements.txt.
    
*   **Environment & Secret:** .env file, python-dotenv. Không hardcode bất cứ secret, API key nào vào code.
    
*   **Testing:** pytest, coverage cho backend; test contract OpShin bằng toolchain CLI.
    
*   **Documentation:** Markdown, docstring chi tiết, có thể bổ sung Sphinx. REST API chuẩn hóa OpenAPI/Swagger.
    
*   **Security:** Flask-Limiter (rate limiting), input validation kỹ càng, CSRF bảo vệ mọi form, JWT/session-based auth cho API bảo mật.
    
*   **Monitoring:** Sentry (hoặc self-hosted), Loguru cho log chi tiết, cảnh báo khi lỗi hệ thống.
    

2\. KIẾN TRÚC & TỔ CHỨC DỰ ÁN
-----------------------------

### 2.1. Tổng quan

Nền tảng Achievo tổ chức module hóa rõ ràng, backend và frontend đều bằng Python (Flask + Jinja2). Toàn bộ nghiệp vụ Web3/NFT/certificate thực hiện qua smart contract OpShin (Python) triển khai trên Cardano. Data off-chain lưu ở Firestore/Postgres, file lớn/metadata lưu IPFS.

### 2.2. Cấu trúc thư mục

```plain
achievo/
├── app/
│   ├── static/        # CSS, JS, images, asset
│   │   └── style.css  # (optional) CSS cơ bản, không Tailwind
│   ├── templates/     # Jinja2 HTML templates (UI)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── certificate.html
│   │   ├── admin.html
│   │   └── ...        # các template khác
│   ├── contract/      # OpShin smart contract code (.py)
│   │   └── cert_nft.py
│   ├── backend.py     # Flask app, route, logic nghiệp vụ
│   ├── opshin_tool/   # Script build/deploy/test contract
│   ├── utils/         # Helper functions, middleware, auth, v.v.
│   └── config.py      # Config chung, load .env
├── tests/
│   ├── unit/
│   ├── integration/
├── docs/              # Tài liệu, specs
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### 2.3. Thành phần chính

#### **Frontend (Flask + Jinja2 UI, không Tailwind, không framework JS)**

*   Giao diện render bằng Jinja2, truyền biến động trực tiếp từ backend Python.
    
*   HTML chia layout (base.html) và các template con cho dashboard, login, admin, certificate lookup…
    
*   CSS cơ bản có thể nhúng vào file style.css hoặc trực tiếp trong template.
    
*   Nếu cần responsive nhanh có thể nhúng Bootstrap CDN (không dùng npm/yarn).
    

#### **Backend (Flask)**

*   Xử lý toàn bộ API, auth, quản lý session/JWT, xác thực người dùng, phân quyền, logging, middleware rate limit, audit trail.
    
*   Kết nối OpShin CLI hoặc toolchain Python để build, deploy, interact contract Cardano.
    
*   Tích hợp Firebase Admin SDK, hoặc ORM (SQLAlchemy) cho dữ liệu off-chain (user, khóa học, log).
    
*   Kết nối IPFS/Pinata lưu metadata NFT, tài liệu chứng chỉ.
    
*   API public/private cho các luồng: xác thực chứng chỉ, marketplace, dashboard, admin.
    

#### **Smart Contract (OpShin – Python)**

*   Viết smart contract bằng Python (OpShin), compile sang Plutus Core, test/deploy với OpShin CLI.
    
*   Quản lý logic NFT, certificate, trạng thái chứng chỉ (issue, revoke, verify), on-chain validation.
    

#### **Data & Storage**

*   **Firestore**: lưu thông tin user, khoá học, log giao dịch, metadata off-chain.
    
*   **IPFS/Pinata**: lưu file lớn, metadata NFT/certificate. Các quyền được cấp phép: pinList, pinFileToIPFS, pinJSONToIPFS.
    
*   **Cardano Blockchain (Preprod/Mainnet)**: lưu tài sản số, NFT, trạng thái hợp đồng; submit transaction qua Koios API.
    
*   **Koios API**: kết nối với Cardano blockchain để đọc/ghi dữ liệu, không phải tự vận hành node. API endpoint: https://preprod.koios.rest/api/v1.
    

3\. YÊU CẦU CHỨC NĂNG CHI TIẾT
------------------------------

### 3.1. Quản lý người dùng cá nhân (Learner)

*   **Đăng ký/xác thực:**Người dùng đăng ký tài khoản qua email, số điện thoại (OTP/Firebase Auth), hoặc đăng nhập trực tiếp bằng Cardano wallet (Nami/Eternl/Flint).Dữ liệu lưu trên Firestore/Postgres, xác thực và session/JWT quản lý qua Flask.
    
*   **Profile cá nhân:**Quản lý thông tin cá nhân (immutable: họ tên, ngày sinh; mutable: email/SĐT). Dữ liệu truy xuất qua backend Flask.
    
*   **Khảo sát định hướng học tập:**Learner có thể thực hiện khảo sát, kết quả lưu/log vào Firestore.
    
*   **Dashboard học tập:**Hiển thị tiến trình, chứng chỉ NFT đã nhận, milestone, phần thưởng (NFT), real-time update (AJAX hoặc page reload).
    
*   **Truy xuất & xác thực chứng chỉ NFT:**Xem, xác minh NFT certificate (metadata IPFS, trạng thái on-chain); backend Flask hoặc Koios API cung cấp endpoint xác thực.
    

### 3.2. Quản lý tổ chức phát hành (Educator/Issuer)

*   **Đăng ký/xác thực tổ chức:**Đăng ký tài khoản, gửi hồ sơ xác minh, phê duyệt thủ công qua dashboard admin, quản lý session bằng Flask.
    
*   **Dashboard tổ chức:**Quản lý học viên, khoá học, chứng chỉ, trạng thái, log, báo cáo từ Firestore/Postgres.
    
*   **Phát hành chứng chỉ NFT:**Tạo và phát hành NFT certificate trên Cardano qua OpShin contract; metadata lưu IPFS, lịch sử lưu Firestore/Postgres.
    
*   **Báo cáo & thống kê:**Truy xuất, export dữ liệu học viên, khoá học, chứng chỉ dưới dạng CSV/JSON/PDF.
    

### 3.3. NFT Credential/Certificate

*   **Tính duy nhất:**Mỗi chứng chỉ/NFT là duy nhất cho mỗi học viên/khoá học, enforced bằng contract và composite key trong DB.
    
*   **Metadata:**Metadata lưu trên IPFS; toàn bộ lịch sử trạng thái ghi log bất biến trên Firestore/Postgres.
    
*   **Dynamic states:**Chứng chỉ cập nhật trạng thái (issued, updated, revoked); mọi thay đổi đều log và chỉ thực hiện on-chain qua backend.
    

### 3.4. Hệ thống phần thưởng học tập (Rewards)

*   **Cấp phát tự động:**Phần thưởng dưới dạng NFT Cardano tự động cấp phát khi đạt milestone học tập, log toàn bộ trên Firestore/Postgres.
    
*   **Hiển thị phần thưởng:**Realtime trên dashboard, thông báo push khi đạt mốc.
    
*   **Anti-fraud:**Logic kiểm soát phát thưởng chỉ một lần/mốc, log mọi sự kiện.
    

### 3.5. Xác thực công khai (Public Certificate Verification)

*   **Tra cứu không cần đăng nhập:**Xác thực chứng chỉ/NFT qua mã hoặc link (public REST API Flask).
    
*   **Kết quả xác thực:**Trả về trạng thái mới nhất, lịch sử; frontend hiển thị hoặc trả JSON.
    
*   **Rate limiting:**API công khai được kiểm soát số lượng request bằng Flask-Limiter.
    

### 3.6. Quản trị hệ thống (Admin)

*   **Dashboard quản trị:**Phê duyệt tổ chức, quản lý user, log thao tác, xử lý sự cố.
    
*   **Audit trail & log lịch sử:**Log toàn bộ thao tác chứng chỉ; log append-only, không sửa, export cho kiểm toán.
    
*   **Export log:**Cho phép export log CSV/PDF.
    

### 3.7. Marketplace & Thanh toán Cardano

*   **Marketplace:**Tổ chức đăng bán khoá học, sản phẩm, dịch vụ; learner mua bằng Cardano token qua giao diện Jinja2.
    
*   **Thanh toán Cardano:**Mọi giao dịch (mua khoá học, dịch vụ, unlock feature) thực hiện qua OpShin contract và Koios API.
    
*   **Quản lý quyền truy cập premium:**Sau khi thanh toán thành công, backend Flask cập nhật quyền truy cập, log & quản lý trên Firestore/Postgres.
    
*   **API premium:**Các API analytics, xác thực premium bảo vệ bằng JWT/logging.
    

4\. YÊU CẦU PHI CHỨC NĂNG
-------------------------

### Bảo mật

*   **Mã hóa dữ liệu nhạy cảm:**Sử dụng thư viện Python hiện đại (cryptography) để mã hóa dữ liệu quan trọng.
    
*   **Firestore Security Rules/Postgres Policy:**Thiết lập rules chặt chẽ, chỉ user/role đúng mới truy cập.
    
*   **Xác thực & phân quyền:**Xác thực qua Firebase Auth/JWT hoặc signature Cardano wallet; REST API luôn kiểm soát quyền truy cập.
    
*   **Rate limiting:**Toàn bộ API (public/private) đều bị rate limit với Flask-Limiter.
    
*   **Audit trail:**Log mọi thao tác hệ trọng, lưu append-only, export cho kiểm toán.
    

### Khả năng mở rộng

*   **Module hóa:**Backend/frontend tách rời, scale hoặc nâng cấp độc lập, mở rộng ra microservice khi cần.
    
*   **Realtime & event-driven:**Sử dụng Flask-SocketIO cho realtime dashboard, Celery/RQ cho background job.
    
*   **Caching:**Caching backend/client hợp lý với Flask-cache/Redis.
    
*   **Background tasks:**Xử lý nền bằng Celery, RQ hoặc cloud functions.
    

### Tính minh bạch

*   **Log immutable:**Lưu append-only, không chỉnh sửa/xoá.
    
*   **Audit/history:**Giao diện truy cứu lịch sử, export log thao tác.
    
*   **Chứng chỉ/giao dịch công khai:**Xác thực trạng thái NFT/certificate qua REST API Flask.
    

### Xác thực công khai

*   **Public API:**Xác thực trạng thái chứng chỉ/NFT qua REST API, trả về lịch sử.
    
*   **Không cần đăng nhập:**API public không yêu cầu tài khoản, nhưng có rate limit và captcha bảo vệ abuse.
    

### Trải nghiệm người dùng

*   **UI/UX:**Giao diện Jinja2 đơn giản, mobile-friendly, có thể dùng Bootstrap CDN nếu cần responsive, không phụ thuộc JS framework.
    
*   **Realtime:**Dashboard cập nhật bằng reload hoặc AJAX đơn giản, Flask-SocketIO nếu muốn realtime.
    
*   **Thông báo rõ ràng:**Flash message, email, hoặc push notification (nếu cần).
    
*   **Hiệu suất tối ưu:**Flask chạy bằng gunicorn/uvicorn, tối ưu code, giảm reload.
    

### Khả năng tích hợp

*   **RESTful API chuẩn:**API backend Flask chuẩn REST, tài liệu OpenAPI đầy đủ.
    
*   **Webhook:**Hỗ trợ webhook sự kiện phát hành chứng chỉ, giao dịch Cardano, reward.
    
*   **Export/Import:**Xuất/nhập dữ liệu CSV, JSON, PDF.
    
*   **SSO:**Đăng nhập một lần qua Firebase Auth hoặc Cardano wallet signature.
    

5\. ROADMAP TRIỂN KHAI (OPSHIN + FLASK + CARDANO + KOIOS)
---------------------------------------------------------

### **Giai đoạn 1: Khởi tạo dự án & hạ tầng cơ bản (3 tuần)**

*   Tạo repository GitHub (module rõ ràng: backend, contract, templates).
    
*   Khởi tạo Flask app, chia module rõ ràng, config CI/CD (GitHub Actions).
    
*   Thiết lập môi trường test Cardano preprod, Koios API Python.
    
*   Thiết kế giao diện base Jinja2 (index, dashboard, login, admin), style CSS cơ bản (không Tailwind).
    
*   Cấu hình môi trường .env, secret management.
    

### **Giai đoạn 2: OpShin contract & User Flow cơ bản (5 tuần)**

*   Viết, test, deploy OpShin contract (NFT mint, xác thực certificate).
    
*   Backend Flask: triển khai luồng đăng ký/xác thực qua email/SĐT/Cardano wallet, quản lý session/JWT, API user/certificate.
    
*   Frontend: các form giao dịch, dashboard học tập, tra cứu chứng chỉ bằng Jinja2 template.
    
*   Tích hợp Koios API Python để truy vấn blockchain, cập nhật trạng thái certificate/NFT.
    

### **Giai đoạn 3: Marketplace, Reward & Advanced Features (6 tuần)**

*   Xây dựng marketplace Flask: đăng bán/mua khoá học, dịch vụ, thanh toán Cardano.
    
*   Triển khai logic phần thưởng tự động (NFT reward khi đạt milestone, trigger backend).
    
*   Giao diện admin quản lý user, tổ chức, giao dịch, log chứng chỉ, export dữ liệu.
    
*   Public API xác thực certificate/NFT, có rate limiting, bảo mật.
    

### **Giai đoạn 4: Tối ưu, audit & release (4 tuần)**

*   Kiểm thử bảo mật backend/frontend, test toàn diện OpShin contract.
    
*   Tối ưu hiệu suất Flask, responsive UI (CSS/Bootstrap), audit toàn bộ codebase.
    
*   Tổng kết, test coverage cao, tài liệu hoá kỹ, release production.
    

### **Các mốc milestone**

*   **M1 (Tuần 3):** Kết nối Flask ↔ Koios/Cardano preprod, deploy test app.
    
*   **M2 (Tuần 8):** Hoàn thành tích hợp OpShin contract và user flow cơ bản (đăng ký/xác thực, dashboard, certificate).
    
*   **M3 (Tuần 14):** Hoàn thành marketplace, auto reward, admin dashboard, public API.
    
*   **M4 (Tuần 18):** Audit bảo mật, kiểm thử toàn diện, release bản chính thức.
    

6\. ĐỀ XUẤT CHUYỂN ĐỔI
----------------------

*   **Toàn bộ backend API, business logic, xác thực, session, rate limiting… thực hiện qua Flask (Python).**
    
*   **Smart contract từ TypeScript/Plu-ts chuyển hoàn toàn sang Python OpShin.**
    
*   **Frontend thay SolidJS/React thành Flask + Jinja2 (SSR), chỉ dùng HTML/CSS truyền thống, không dùng Tailwind, không dùng JS framework. Có thể dùng Bootstrap CDN nếu cần responsive.**
    
*   **CI/CD chuyển sang Github Actions/Python-based (build, test, deploy Flask app và test contract OpShin).**
    
*   **Không sử dụng bất kỳ service nào phụ thuộc Node.js trong production.**
    
*   **Tài liệu hóa lại API theo chuẩn OpenAPI, docstring Python chuẩn, đầy đủ cho từng endpoint.**
    
*   **Mọi tích hợp Koios, IPFS/Pinata, Firestore hoặc Postgres đều qua thư viện Python.**
    
*   **Mọi logging, alert, monitoring dùng hệ sinh thái Python (Sentry, Loguru, v.v.).**