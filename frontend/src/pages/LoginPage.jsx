export default function LoginPage() {
  return (
    <section className="mx-auto max-w-md rounded-[2rem] border border-white/10 bg-white/5 p-6">
      <p className="text-sm uppercase tracking-[0.3em] text-cyan-300">Auth</p>
      <h2 className="mt-3 text-3xl font-semibold">JWT login for bookmarking.</h2>
      <p className="mt-3 text-sm leading-6 text-slate-300">
        Use `/api/auth/register/`, `/api/auth/token/`, and `/api/auth/me/` to build the full login flow.
      </p>
    </section>
  );
}
