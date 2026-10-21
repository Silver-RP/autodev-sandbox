# ROADMAP auto-dev (sandbox)

Nguyên tắc: ưu tiên auto-dev nhưng không làm sai mục tiêu dự án thử.

Cập nhật: 2026-10-21 (supervisor, sau khi merge R16).

**Lộ trình chi tiết:**
- `docs/goals/due-overdue/roadmap.md`: R1–R2, xong.
- `docs/goals/lazy-landing/roadmap.md`: R3–R13. Tiêu chí ở `criteria.md` cùng thư mục, spec thiết kế ở `docs/design/lazy-landing.md`.

## Tổng quan R1–R17

| Mốc | Mục tiêu | Tên | Trạng thái | Task | Chỉ số | Phụ thuộc | Ước tính USD | Thực tế |
|---|---|---|---|---|---|---|---|---|
| R1 | due-overdue | Hạn chót (`add --due`, `todo due`, cột hạn) | merged 2026-10-15, PR #5 | 3 | A1, A3, A4 | – | 4 | chế độ B: worker 4,2 phút / 0,71 USD; supervisor 2,5 phút / 0,75 USD |
| R2 | due-overdue | Lọc việc quá hạn (`todo overdue`) + H-01 | merged 2026-10-16, PR #8 | 3 | A2, A5, A3, A4 | R1 | 4 | chế độ B: worker 4 phút / 0,72 USD; supervisor 2,8 phút / 0,80 USD |
| R3 | lazy-landing | Landing page dùng được (`site/` 4 phần, test cấu trúc, smoke HTTP) | merged 2026-10-16, PR #14 | 3 | L1, L5, L3, L4 | – | 1,6 | chế độ A: ~5 phút cả mốc; USD chưa đo |
| R4 | lazy-landing | Công cụ nhìn (`screenshot.py` 360 thật qua iframe / 1280, sáng / tối; `page_metrics.py`) + luật tài nguyên mới | merged 2026-10-16, PR #20 | 4 | D1, L2 | R3 | 1,8 | chế độ B: worker 20 phút / 1,06 USD; supervisor ~0,77 USD (tạm) |
| R5 | lazy-landing | Ba hướng thiết kế, dừng chờ chọn | **cắt** 2026-10-16: leader chọn trước hướng "Quán cóc đầu ngõ" | – | (D2 → R6) | – | – | – |
| R6 | lazy-landing | Dựng trang theo spec "Quán cóc đầu ngõ" (test spec, token, font, SVG, nội dung) | merged 2026-10-16, PR #22 | 5 | D2, D3, L1 | R4 | 3,3 | chế độ B: worker 44 phút / 2,25 USD; supervisor ~0,89 USD (tạm) |
| R7 | lazy-landing | Chuyển động (GSAP qua CDN, SRI) + một tương tác; an toàn khi không JS | merged 2026-10-16, PR #24 | 3 | D6 | R6 | 2,3 | chế độ B: worker 34 phút / 1,38 USD; supervisor ~1,00 USD (tạm) |
| R8 | lazy-landing | Chế độ tối + truy cập (tương phản AA, focus, `aria`, không tràn) | merged 2026-10-16, PR #26 | 4 | D4, D5 | R6 | 2,8 | chế độ B: worker 43 phút / 1,31 USD; supervisor ~1,09 USD (tạm) |
| R12 | lazy-landing | Mở rộng nội dung (FAQ, 3 dự án "ví dụ") | merged 2026-10-16, PR #28 | 3 | E4 | R6 | 2,3 | chế độ B: worker 31 phút / 0,99 USD; supervisor ~1,16 USD (tạm) |
| R9 | lazy-landing | SEO và chia sẻ (OG, `og.png`, favicon, sitemap, JSON-LD) | merged 2026-10-16, PR #30 (lần 2, sau (b) dev-05, dev-06) | 4 (+2) | E1 | R6, R12 | 1,8 | chế độ B, 2 lượt: worker 64 phút; worker + supervisor 3,44 USD + ~1 (phiên duyệt lần 2, tạm) |
| R13 | lazy-landing | Song ngữ Việt/Anh (`site/en/`, `hreflang`) | merged 2026-10-16, PR #33 | 3 | E5 | R12, R9 | 1,9 | chế độ B: worker 36 phút; worker + supervisor 1,40 + ~1,26 USD (tạm) |
| R10 | lazy-landing | Hiệu năng (Lighthouse mobile ≥ 90 / 95, ≤ 300 KB) | merged 2026-10-16, PR #35 | 3 | E2 | R7, R8, R13 | 1,5 | chế độ B: worker 42 phút; worker + supervisor 1,24 + ~1,26 USD (tạm) |
| R14 | lazy-landing | Cứng hoá công cụ đo và luật tài nguyên (audit H-06, H-07, H-09, H-10, H-15, H-17) | merged 2026-10-21, PR #44 | 4 | D1, L2, E2, L3 | R11 | 2,0 | chế độ B: worker 41 phút; worker + supervisor 1,35 + ~1,27 USD (tạm) |
| R11 | lazy-landing | Triển khai GitHub Pages + smoke URL thật | merged 2026-10-20, PR #40; E3 đạt trên `https://silver-rp.github.io/autodev-sandbox/` | 3 | E3 | R10 | 1,3 | chế độ B: worker 33 phút; worker + supervisor 1,04 + ~1,26 USD (tạm) |
| R15 | lazy-landing | Hoàn thiện site: 360 giữ chấm dẫn + nút header, font tải thật, reduced-motion CSS, test cả bản Anh, ly hero (audit H-03, H-04, H-05, H-11, H-20; H-21 chuyển mốc công cụ) | merged 2026-10-21, PR #48 | 4 | D3, D4, D6, E5, L3 | R14 | 2,0 | chế độ B: worker 85 phút; worker + supervisor 2,53 + ~1,28 USD (tạm) |
| R17 | due-overdue | Cứng hoá todo CLI: id ASCII, tiêu đề rỗng/xuống dòng, `done` id không có, JSON hỏng exit 2, ghi qua symlink, khoá `flock` (audit H-26, H-13, H-18) | merged 2026-10-21, PR #52 | 3 | A1, A2, A3, A4 | R2 | 1,5 | chế độ B: worker 60 phút; worker + supervisor 1,20 + ~1,33 USD (tạm) |
| R16 | lazy-landing | Công cụ đo và deploy chặt: screenshot kiểm HTTP, overflow `scrollWidth`, `lh_check` thiếu `index.html`, smoke fetch, Pages chờ test, exit 2 lỗi công cụ, spec hero theo trang đã duyệt (audit H-22..H-25, H-27 một phần, H-28, H-29) | merged 2026-10-21, PR #56; E3 đạt @ `ff8c12f` | 4 | D1, D2, D4, E2, E3, L3 | R15 | 2,5 (plan 3,2) | chế độ B: worker 90 phút; worker + supervisor 2,16 + ~1,34 USD (tạm) |

**Tổng:**
- Đã xong: R1–R4, R6–R17, 58 task. Mọi mốc trong hai `goal.json` đã `done`.
- Còn lại: chưa có mốc lập sẵn. Đề xuất (audit 2026-10-21-2): mốc công cụ tiếp (H-21, H-27 phần còn lại, H-30, H-32, H-33, H-40), R18 todo (H-34..38, H-41), R19 kiểm chứng (H-31, H-39, H-42); cần leader lập roadmap/goal.
- Mục tiêu `lazy-landing` hiện đạt 17/17 chỉ số (sau R11; D7 leader duyệt 2026-10-20); `due-overdue` đạt 5/5.

## Chạy tiếp (sau khi reset hạn mức)

Rà soát ngày 2026-10-16 (phiên leader, chỉ đọc) xác nhận chuỗi chạy được không cần người:
- đủ 8 plan trên `origin/main`;
- hai worktree `autodev-sandbox-autodev` và `autodev-sandbox-supervisor` sạch;
- chế độ B đã chạy trọn R1, R2;
- thứ tự lệnh khớp phụ thuộc;
- `lighthouse@12.8.2` đã có trong cache `npx`.

```
/autodev:run --audit-every 0 R4 R6 R7 R8 R12 R9 R13 R10
/autodev:audit R4 R6 R7 R8 R12 R9 R13 R10        # một lần ở cuối, ~5–6 USD
```

`--audit-every 0` là bắt buộc. Mặc định runner audit sau mỗi 2 mốc, và `.autodev/runs/audit.json` còn sẵn `R1, R2`, nên sẽ có 4 lần audit ngoài kế hoạch (khoảng +22 USD, +50 phút).

### Ước lượng thời gian
Số đo chế độ B (R1, R2): khoảng 8 phút / mốc 3 task (worker ~4, supervisor ~2,7, merge hồ sơ ~1,3), khoảng 1,5 USD. Mốc có Chrome / ảnh nhân thời gian worker ×2–2,5 (giả định); R10 cộng thời gian Lighthouse.

| R4 | R6 | R7 | R8 | R12 | R9 | R13 | R10 | Tổng |
|---|---|---|---|---|---|---|---|---|
| ~17 phút | ~24 | ~16 | ~20 | ~13 | ~13 | ~13 | ~21 | **~2,3 giờ máy** (~2,7 giờ nếu phải làm lại) |

- **Thời gian thực khoảng 6–11 giờ.** Theo số đo của repo plugin, 1,72 USD ≈ 16–22% cửa sổ 5 giờ, nên một cửa sổ chứa khoảng 8–10 USD. Chuỗi khoảng 18 USD chạm giới hạn 1–2 lần; runner tự chờ reset + 5 phút rồi chạy tiếp.
- Chạm **hạn mức tuần** thì runner dừng hẳn (exit 3, `.autodev/runs/STOPPED.md`).

### Điều kiện và rủi ro còn lại
- Máy cắm sạc, mở nắp: `caffeinate -i` không giữ máy thức khi gập nắp.
- Supervisor (Opus) có thể trả một mốc thiết kế về kèm task (b). Runner dừng exit 4 và cần người xem; đây là cổng chất lượng.
- Phiên headless chạy ở `--permission-mode auto`, không có người duyệt. Lệnh mạng (Google Fonts, CDN, SRI) hoặc Chrome có thể bị từ chối; khi đó task BLOCKED và runner dừng.
- R10: điểm Lighthouse có thể dao động. Plan dùng trung vị 3 lần; nếu không đạt thì mốc BLOCKED.
- Theo dõi: `.autodev/runs/run.log`; khi dừng: `.autodev/runs/STOPPED.md`.

## Việc chỉ người làm
| Khi | Việc |
|---|---|
| ~~Sau R5~~ | ~~Chọn hướng thiết kế~~: đã chọn 2026-10-16 (hướng 2 "Quán cóc đầu ngõ") |
| Sau chuỗi (R10 xong) | Duyệt bằng mắt bản Việt và bản Anh (D7): ghi `Leader duyệt: đạt` hoặc ý sửa vào `docs/design/lazy-landing.md` |
| Trước R11 | Bật GitHub Pages (repo private cần gói trả phí, hoặc đổi sang public), cho biết URL; rồi `/autodev:run R11` |
| Bất kỳ lúc nào | Thay tên, email, giá giữ chỗ; tuỳ chọn thêm `screenshot.py` và L5 vào `smoke` của `.autodev/config.json` |

## Lịch sử quyết định chính
- **2026-10-15:** mục tiêu `due-overdue` (PR #2); R1 merge.
- **2026-10-16:**
  - R2 merge, `due-overdue` 5/5.
  - Mục tiêu `lazy-landing` bản 1 "tối giản" (PR #12); R3 merge (PR #14).
  - Leader xem R3 thấy "xấu quá, chỉ có text": cài plugin `frontend-design`, sửa mục tiêu thành bản 2 "đẹp, có cá tính" kèm mở rộng SEO, hiệu năng, song ngữ, triển khai (PR #15).
  - Plan R4 (PR #16), R5–R13 + spec thiết kế (PR #17); R5 cắt; sửa R6 (PR #18).
