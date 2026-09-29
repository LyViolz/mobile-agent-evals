import 'package:flutter_test/flutter_test.dart';
import 'package:reminder_fixture/reminder_schedule.dart';

void main() {
  test('same weekday before the reminder stays today', () {
    final now = DateTime(2026, 9, 28, 8); // Monday.
    expect(
      nextWeeklyReminder(now, DateTime.monday, 9, 30),
      DateTime(2026, 9, 28, 9, 30),
    );
  });

  test('same weekday after the reminder moves to next week', () {
    final now = DateTime(2026, 9, 28, 10); // Monday.
    expect(
      nextWeeklyReminder(now, DateTime.monday, 9, 30),
      DateTime(2026, 10, 5, 9, 30),
    );
  });

  test('exact reminder minute moves to next week', () {
    final now = DateTime(2026, 9, 28, 9, 30);
    expect(
      nextWeeklyReminder(now, DateTime.monday, 9, 30),
      DateTime(2026, 10, 5, 9, 30),
    );
  });

  test('a different weekday crosses the month boundary', () {
    final now = DateTime(2026, 9, 29, 18); // Tuesday.
    expect(
      nextWeeklyReminder(now, DateTime.thursday, 9, 30),
      DateTime(2026, 10, 1, 9, 30),
    );
  });

  test('invalid weekday is rejected', () {
    expect(
      () => nextWeeklyReminder(DateTime(2026, 9, 28), 8, 9, 30),
      throwsRangeError,
    );
  });
}
