import "./globals.css"

export const metadata = {
  title: "AI Local Business Intelligence Agent",
  description: "Autonomous multi-agent local market research"
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
