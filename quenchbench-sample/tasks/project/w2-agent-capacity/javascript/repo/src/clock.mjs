// A clock that only moves when told to. The helpdesk never reads the system time.
export class ManualClock {
  constructor(start = 0) {
    this._now = start;
  }

  now() {
    return this._now;
  }

  advance(minutes) {
    this._now += minutes;
    return this._now;
  }

  set(minutes) {
    this._now = minutes;
  }
}
