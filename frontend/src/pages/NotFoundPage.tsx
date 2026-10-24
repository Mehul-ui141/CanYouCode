import { Link } from "react-router-dom";
import Container from "../components/layout/Container";

export default function NotFoundPage() {
  return (
    <Container>
      <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
        <span className="text-6xl">🔥</span>
        <h2 className="text-3xl font-black text-zinc-200">404</h2>
        <p className="text-zinc-400">
          This page doesn't exist. Maybe your code deleted it?
        </p>
        <Link
          to="/"
          className="text-sm text-red-400 hover:text-red-300 underline underline-offset-4"
        >
          Go back home
        </Link>
      </div>
    </Container>
  );
}
