/// Returns the next occurrence of a weekly reminder in local time.
DateTime nextWeeklyReminder(DateTime now, int weekday, int hour, int minute) {
  if (weekday < DateTime.monday || weekday > DateTime.sunday) {
    throw RangeError.range(
      weekday,
      DateTime.monday,
      DateTime.sunday,
      'weekday',
    );
  }
  if (hour < 0 || hour > 23) {
    throw RangeError.range(hour, 0, 23, 'hour');
  }
  if (minute < 0 || minute > 59) {
    throw RangeError.range(minute, 0, 59, 'minute');
  }

  final daysAhead = (weekday - now.weekday + 7) % 7;
  return DateTime(now.year, now.month, now.day + daysAhead, hour, minute);
}
