import { ValueError } from "./errors.ts";

function realDay(y: number, m: number, d: number): boolean {
  const leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return y >= 1 && m >= 1 && m <= 12 && d >= 1 && d <= (days[m - 1] as number);
}
export function isDay(text: string): boolean {
  return (
    /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/u.test(text) &&
    realDay(Number(text.slice(0, 4)), Number(text.slice(5, 7)), Number(text.slice(8, 10)))
  );
}
export function isStamp(text: string): boolean {
  return (
    /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}$/u.test(text) &&
    isDay(text.slice(0, 10)) &&
    Number(text.slice(11, 13)) < 24 &&
    Number(text.slice(14, 16)) < 60 &&
    Number(text.slice(17, 19)) < 60 &&
    Number(text.slice(20, 22)) * 60 + Number(text.slice(23, 25)) < 1440
  );
}
export function instant(stamp: string): number {
  if (!isStamp(stamp)) throw new ValueError(`not a stamp: ${stamp}`);
  const y = Number(stamp.slice(0, 4)),
    m = Number(stamp.slice(5, 7)),
    d = Number(stamp.slice(8, 10));
  const year = y - (m <= 2 ? 1 : 0),
    era = Math.floor(year / 400),
    yoe = year - era * 400;
  const doy = Math.floor((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5) + d - 1;
  const days =
    era * 146097 + yoe * 365 + Math.floor(yoe / 4) - Math.floor(yoe / 100) + doy - 719468;
  const offset =
    (Number(stamp.slice(20, 22)) * 60 + Number(stamp.slice(23, 25))) * (stamp[19] === "-" ? -1 : 1);
  return (
    ((days * 24 + Number(stamp.slice(11, 13))) * 3600 +
      Number(stamp.slice(14, 16)) * 60 +
      Number(stamp.slice(17, 19)) -
      offset * 60) *
    1000
  );
}
export function compareStamps(a: string, b: string): number {
  return instant(a) - instant(b);
}
