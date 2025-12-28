// app/page.tsx (server component)
import Home from "./Home";

export const metadata = {
  title: "UW-Madison Schedule to iCal Converter",
  openGraph: {
    title: "UW-Madison Schedule to iCal Converter",
  },
};

export default function Page() {
  return <Home />; // Home can remain a "use client" component
}
