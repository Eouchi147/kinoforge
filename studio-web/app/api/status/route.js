import { bestModels } from '@/lib/openrouter';
export const dynamic = 'force-dynamic';
export async function GET() {
  const openrouter = Boolean(process.env.OPENROUTER_API_KEY), github = Boolean(process.env.GITHUB_TOKEN);
  let models = [];
  try { models = await bestModels({ needImages: false }); } catch {}
  return Response.json({ openrouter, github, models, budget: (process.env.KF_BUDGET || 'free').toLowerCase() });
}
