export function RegisterPage() {
    return (
      <div className="max-w-md mx-auto py-20 px-4">
        <div className="bg-white p-8 rounded-2xl shadow-xl">
          <h2 className="text-3xl font-bold mb-8 text-center">Login</h2>
          <form className="space-y-6">
            <input
              type="email"
              placeholder="Email"
              className="w-full p-3 border rounded-lg"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full p-3 border rounded-lg"
            />
            <button className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg">
              Login
            </button>
          </form>
        </div>
      </div>
    )
  }