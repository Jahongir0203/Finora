import 'package:finora/common/extensions/format_extensions.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('money', () {
    expect(24850000.toMoney(), '24 850 000');
    expect(24850000.toUzs(), '24 850 000 UZS');
    expect(12500000.toMoney(sign: true), '+12 500 000');
    expect((-186400).toMoney(sign: true), '−186 400');
    expect(0.toMoney(sign: true), '0');
    expect(999.4.toMoney(), '999');
  });

  test('short', () {
    expect(1200000.toShort(), '1.2M');
    expect(10000000.toShort(), '10M');
    expect(850000.toShort(), '850K');
    expect(2500000000.toShort(), '2.5B');
    expect(500.toShort(), '500');
    expect(5460000.toShort(), '5.46M');
    expect(13000000.toShort(), '13M');
  });

  test('phone & card', () {
    expect('+998901234567'.toPhone(), '+998 90 123 45 67');
    expect('998901234567'.toMaskedPhone(), '+998 90 *** ** 67');
    expect('8600 1234 5678 4821'.toMaskedCard(), '•••• 4821');
  });
}
