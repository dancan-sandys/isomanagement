// Suppress d3-dispatch TypeScript errors
declare module '@types/d3-dispatch' {
  export interface Dispatch<This = any, EventMap = any> {
    on(typenames: string): this;
    on(typenames: string, listener: null): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void, capture?: boolean): this;
  }

  export function dispatch<This = any, EventMap = any>(): Dispatch<This, EventMap>;
}

declare module 'd3-dispatch' {
  export interface Dispatch<This = any, EventMap = any> {
    on(typenames: string): this;
    on(typenames: string, listener: null): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void, capture?: boolean): this;
  }

  export function dispatch<This = any, EventMap = any>(): Dispatch<This, EventMap>;
}

// Override the problematic d3-dispatch file directly
declare module '*/node_modules/@types/d3-dispatch/index.d.ts' {
  export interface Dispatch<This = any, EventMap = any> {
    on(typenames: string): this;
    on(typenames: string, listener: null): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void, capture?: boolean): this;
  }

  export function dispatch<This = any, EventMap = any>(): Dispatch<This, EventMap>;
}
