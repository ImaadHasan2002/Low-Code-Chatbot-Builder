import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Protect all authenticated app routes. Note: route groups like
// "(dashboard)" do not appear in URLs, so each top-level page is listed.
export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')

  if (!token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/analytics/:path*',
    '/knowledge-base/:path*',
    '/playground/:path*',
    '/settings/:path*',
    '/onboarding/:path*',
  ],
}
