import { seat, account } from '@/lib/agents';
import CREW from '@/lib/crew.json';
export const dynamic = 'force-dynamic';
export async function GET() {
  const openrouter = Boolean(process.env.OPENROUTER_API_KEY), github = Boolean(process.env.GITHUB_TOKEN);
  let seats = {}, acct = null;
  if (openrouter) {
    const names = ['head', 'deputy', 'crew', 'eyes', 'ears', 'free'];
    const chains = await Promise.all(names.map((n) => seat(n).catch(() => [])));
    names.forEach((n, i) => { seats[n] = chains[i]; });
    acct = await account();
  }
  return Response.json({ openrouter, github, seats, models: seats.head || [], caps: CREW.caps, account: acct });
}
