import { Mail, MessageSquare, Send } from 'lucide-react';

export function Contact() {
  return (
    <section className="py-20 px-6 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-center text-4xl mb-4 text-gray-900">Need help?</h2>
        <p className="text-center text-gray-600 mb-12">
          Get in touch for support or questions
        </p>

        <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-200">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="mb-6 text-gray-900">Contact Information</h3>
              <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-gray-900">Email Support</p>
                  <p className="text-gray-600 text-sm">kush3489t@gmail.com</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="mb-6 text-gray-900">Quick Message</h3>
              <form className="space-y-4">
                <input
                  type="email"
                  placeholder="Your email"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <textarea
                  placeholder="Your message"
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
                <button
                  type="submit"
                  className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}