import ApiStatus from "@/components/ApiStatus";

const steps = [
  {
    title: "Rate your units",
    body: "Mark each unit Weak, OK, or Strong, and click the hours you're free.",
  },
  {
    title: "Get an opposite",
    body: "We pair you with a classmate who is strong where you're weak, and the other way around.",
  },
  {
    title: "Swap for 45 minutes",
    body: "Your session room has a call, a shared whiteboard, and a plan for who teaches what.",
  },
];

const safety = [
  "School email sign-in only",
  "First names only",
  "Both students must accept",
  "Camera off by default",
  "Report and Block always one click away",
];

export default function Home() {
  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-12 px-4 py-16">
      <header className="flex flex-col gap-4">
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          StudySwap
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-balance">
          Pairs students who can teach each other, then gives them exactly what
          to do in their first session.
        </h1>
        <ApiStatus />
      </header>

      <section className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold">How it works</h2>
        <ol className="grid gap-4 sm:grid-cols-3">
          {steps.map((step, i) => (
            <li key={step.title} className="rounded-lg border border-slate-200 p-4 dark:border-slate-700">
              <span className="font-mono text-sm text-slate-500">{i + 1}</span>
              <h3 className="font-semibold">{step.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">Safety</h2>
        <ul className="list-disc pl-5 text-slate-700 dark:text-slate-300">
          {safety.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <p className="text-sm text-slate-500">
        Placeholder landing page (Phase 0). Sign-in, onboarding, and matching
        come in later phases.
      </p>
    </main>
  );
}
