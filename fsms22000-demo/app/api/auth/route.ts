import { NextRequest, NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import { getSession } from '@/lib/session'
import { listRecords } from '@/lib/db'

type User = { id: string; name: string; email: string; role: string; passwordHash?: string }

enum HttpStatus { Unauthorized = 401 }

export async function POST(req: NextRequest) {
  const body = (await req.json()) as { email: string; password: string }
  const { email, password } = body
  const { items: users } = await listRecords<User>('users', { query: { email } as Partial<User> })
  const user = users[0]
  if (!user || !user.passwordHash) {
    return NextResponse.json({ error: 'Invalid credentials' }, { status: HttpStatus.Unauthorized })
  }
  const ok = await bcrypt.compare(password, user.passwordHash)
  if (!ok) return NextResponse.json({ error: 'Invalid credentials' }, { status: HttpStatus.Unauthorized })
  const session = await getSession()
  session.user = { id: user.id, name: user.name, email: user.email, role: user.role }
  await session.save()
  return NextResponse.json({ user: session.user })
}

export async function DELETE() {
  const session = await getSession()
  session.destroy()
  return NextResponse.json({ ok: true })
}


