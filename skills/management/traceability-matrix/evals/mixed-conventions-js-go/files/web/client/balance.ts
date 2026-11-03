export interface Balance {
  posted: number;
  pending: number;
}

// @req R-020
export async function fetchBalance(memberId: string): Promise<Balance> {
  const res = await fetch(`/api/members/${memberId}/balance`);
  const body = await res.json();
  return { posted: body.posted_points, pending: body.pending_points };
}
