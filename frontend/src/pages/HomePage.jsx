const sampleCards = [
  {
    category: "business",
    title: "Market-moving updates, distilled",
    summary:
      "Public article browsing will be powered by the Django API, with Gemini summaries layered on top of scraped RSS-linked content.",
  },
  {
    category: "tech",
    title: "Niche feeds, not generic clutter",
    summary:
      "Each source belongs to either business or tech, keeping the homepage focused instead of turning into a broad news firehose.",
  },
];

export default function HomePage() {
  return (
    <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur">
        <p className="mb-3 text-sm uppercase tracking-[0.3em] text-cyan-300">Public Feed</p>
        <h2 className="max-w-2xl text-3xl font-semibold tracking-tight">
          Your React frontend can read all articles without login, then promote sign-in only when a user wants to save a note.
        </h2>
      </div>

      <div className="rounded-[2rem] border border-cyan-300/20 bg-cyan-300/10 p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan-200">Stack</p>
        <ul className="mt-4 space-y-3 text-sm text-slate-200">
          <li>Django REST Framework API</li>
          <li>SQLite database</li>
          <li>Celery and Redis background jobs</li>
          <li>Tailwind interface layer</li>
        </ul>
      </div>

      {sampleCards.map((card) => (
        <article
          key={card.title}
          className="rounded-[1.75rem] border border-white/10 bg-slate-950/40 p-6 transition hover:-translate-y-1 hover:border-cyan-300/40"
        >
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">{card.category}</p>
          <h3 className="mt-3 text-2xl font-medium">{card.title}</h3>
          <p className="mt-3 text-sm leading-6 text-slate-300">{card.summary}</p>
        </article>
      ))}
    </section>
  );
}
