interface Store { trees(): Promise<number>; hold(n: number): Promise<number> }
export class Sqlite implements Store { async trees() { return 1; } }
