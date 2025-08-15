import { NextRequest, NextResponse } from 'next/server'
import { getRecord, updateRecord, deleteRecord, CollectionName } from '@/lib/db'

type GenericRecord = Record<string, unknown>

function parsePath(req: NextRequest): { collection: CollectionName; id: string } {
  const segs = new URL(req.url).pathname.split('/').filter(Boolean)
  const id = segs[segs.length - 1]
  const collection = segs[segs.length - 2] as CollectionName
  return { collection, id }
}

export async function GET(req: NextRequest) {
  const { collection, id } = parsePath(req)
  const rec = await getRecord<GenericRecord>(collection, id)
  if (!rec) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(rec)
}

export async function PUT(req: NextRequest) {
  const { collection, id } = parsePath(req)
  const body = (await req.json()) as Partial<GenericRecord>
  const rec = await updateRecord<GenericRecord>(collection, id, body)
  if (!rec) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(rec)
}

export async function DELETE(req: NextRequest) {
  const { collection, id } = parsePath(req)
  const ok = await deleteRecord(collection, id)
  return NextResponse.json({ ok })
}


