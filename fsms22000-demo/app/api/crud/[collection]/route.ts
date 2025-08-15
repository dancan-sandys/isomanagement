import { NextRequest, NextResponse } from 'next/server'
import { listRecords, createRecord, CollectionName } from '@/lib/db'
import { paginationSchema } from '@/lib/schemas'

type GenericRecord = Record<string, unknown>

function parseCollection(req: NextRequest): CollectionName {
  const segs = new URL(req.url).pathname.split('/').filter(Boolean)
  return segs[segs.length - 1] as CollectionName
}

export async function GET(req: NextRequest) {
  const collection = parseCollection(req)
  const url = new URL(req.url)
  const parsed = paginationSchema.safeParse(Object.fromEntries(url.searchParams))
  const { limit, offset, search, sortBy, sortDir } = parsed.success ? parsed.data : {}
  const searchKeys = ['name', 'title', 'productName', 'code', 'type', 'department']
  const { items, total } = await listRecords<GenericRecord>(collection, { limit, offset, search, searchKeys, sortBy, sortDir })
  return NextResponse.json({ items, total })
}

export async function POST(req: NextRequest) {
  const collection = parseCollection(req)
  const body = (await req.json()) as GenericRecord
  const created = await createRecord<GenericRecord>(collection, body)
  return NextResponse.json(created)
}


