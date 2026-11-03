export interface Txn {
  id: string;
  postedAt: string;
  points: number;
}

// @req R-021
export function newestFirst(txns: Txn[]): Txn[] {
  return [...txns].sort((a, b) => b.postedAt.localeCompare(a.postedAt));
}
