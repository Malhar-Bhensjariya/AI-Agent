
export default function LandingPage() {
  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="text-center space-y-8 py-20">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
          AI Research Analyst
        </h1>

        <div className="grid gap-6 md:grid-cols-2 mt-12">
          <div className="p-6 rounded-xl bg-white shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Upload Data</h3>
            <p className="text-gray-600">CSV/Excel files supported</p>
          </div>

          <div className="p-6 rounded-xl bg-white shadow-lg">
            <h3 className="text-xl font-semibold mb-2">Ask Questions</h3>
            <p className="text-gray-600">Get instant insights from your data</p>
          </div>
        </div>
      </div>
    </div>
  );
}
