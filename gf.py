"""
Nhân hai đa thức trong trường hữu hạn GF(2^n).

Biểu diễn: mỗi đa thức bậc < n trên GF(2) là một số nguyên, bit i = hệ số của x^i.
  Ví dụ: x^3 + x + 1  ->  0b1011  ->  0x0B
Phép cộng trong GF(2^n) chính là XOR.
"""

# Đa thức tối giản (bao gồm cả số hạng x^n)
IRREDUCIBLE = {
    4: 0b10011,        # x^4 + x + 1
    8: 0b100011011,    # x^8 + x^4 + x^3 + x + 1  (đa thức của AES, 0x11B)
}


def poly_to_str(a: int) -> str:
    """Chuyển số nguyên thành chuỗi đa thức, ví dụ 0b1011 -> 'x^3 + x + 1'."""
    if a == 0:
        return "0"
    terms = []
    for i in range(a.bit_length() - 1, -1, -1):
        if (a >> i) & 1:
            terms.append("1" if i == 0 else "x" if i == 1 else f"x^{i}")
    return " + ".join(terms)


# ---------- Cách 1: tách làm 2 bước (dễ hiểu, đúng theo lý thuyết) ----------

def poly_mul(a: int, b: int) -> int:
    """Bước 1: nhân hai đa thức trên GF(2) (carry-less), chưa rút gọn."""
    result = 0
    while b:
        if b & 1:
            result ^= a      # cộng (XOR) a đã dịch vào kết quả
        a <<= 1              # nhân a với x
        b >>= 1
    return result


def poly_mod(a: int, m: int) -> int:
    """Bước 2: chia a cho m trên GF(2), lấy phần dư."""
    deg_m = m.bit_length() - 1
    while a.bit_length() - 1 >= deg_m:
        shift = (a.bit_length() - 1) - deg_m
        a ^= m << shift      # trừ (XOR) m * x^shift
    return a


def gf_mul(a: int, b: int, n: int) -> int:
    """Nhân a, b trong GF(2^n) theo đa thức tối giản IRREDUCIBLE[n]."""
    return poly_mod(poly_mul(a, b), IRREDUCIBLE[n])


# ---------- Cách 2: nhân và rút gọn dần (russian peasant, như AES) ----------

def gf_mul_fast(a: int, b: int, n: int) -> int:
    m = IRREDUCIBLE[n]
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a >> n:           # bậc a đạt n -> rút gọn
            a ^= m
        b >>= 1
    return result


# ---------- Kiểm tra đa thức tối giản (bổ sung) ----------

def is_irreducible(m: int) -> bool:
    """Đa thức m (bậc n) là tối giản nếu không chia hết cho mọi đa thức bậc 1..n/2."""
    n = m.bit_length() - 1
    for d in range(2, 1 << (n // 2 + 1)):
        if d.bit_length() - 1 >= 1 and poly_mod(m, d) == 0:
            return False
    return True


if __name__ == "__main__":
    # Kiểm tra tính tối giản
    for n, m in IRREDUCIBLE.items():
        print(f"GF(2^{n}): m(x) = {poly_to_str(m)}  -> tối giản: {is_irreducible(m)}")
    print()

    # Ví dụ GF(2^4)
    a, b = 0b0111, 0b0110   # x^2+x+1 và x^2+x
    c = gf_mul(a, b, 4)
    print(f"GF(2^4): ({poly_to_str(a)}) * ({poly_to_str(b)}) = {poly_to_str(c)}  (0x{c:X})")

    # Ví dụ GF(2^8): ví dụ kinh điển trong AES, 0x57 * 0x83 = 0xC1
    a, b = 0x57, 0x83
    c = gf_mul(a, b, 8)
    print(f"GF(2^8): ({poly_to_str(a)}) * ({poly_to_str(b)}) = {poly_to_str(c)}  (0x{c:02X})")
    assert c == 0xC1

    # Đối chiếu hai cách cài đặt trên toàn bộ cặp phần tử
    for n in (4, 8):
        size = 1 << n
        assert all(gf_mul(x, y, n) == gf_mul_fast(x, y, n)
                   for x in range(size) for y in range(size))
        # Mỗi phần tử khác 0 phải có nghịch đảo -> chứng tỏ đây là một trường
        for x in range(1, size):
            assert any(gf_mul(x, y, n) == 1 for y in range(1, size))
        print(f"GF(2^{n}): hai cách cài đặt khớp nhau, mọi phần tử ≠ 0 đều có nghịch đảo ✔")
