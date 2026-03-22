export default function BookmarksPage() {
  return (
    <section className="rounded-[2rem] border border-white/10 bg-white/5 p-6">
      <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Bookmarks</p>
      <h2 className="mt-3 text-3xl font-semibold">Private notes live here.</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
        Connect this page to `GET /api/bookmarks/` and `POST /api/bookmarks/` once you install the frontend dependencies.
      </p>
    </section>
  );
}
