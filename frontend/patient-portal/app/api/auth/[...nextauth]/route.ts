import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Demo credentials — replace with real DB check in production
        if (
          credentials?.email === "demo@mindbridge.health" &&
          credentials?.password === "MindBridge2026!"
        ) {
          return {
            id: "1",
            email: "demo@mindbridge.health",
            name: "Dr. Demo Clinician",
            role: "case_manager",
          };
        }
        return null;
      },
    }),
  ],
  session: {
    strategy: "jwt",
    maxAge: 8 * 60 * 60, // 8 hours — one clinical shift (HIPAA alignment)
  },
  pages: {
    signIn: "/", // Redirect to login page
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).role = token.role;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };