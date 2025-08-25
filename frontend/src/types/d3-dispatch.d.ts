// Custom type declarations to fix d3-dispatch TypeScript issues
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
  export interface Dispatch<T = any> {
    on(typenames: string): (listener: any) => Dispatch<T>;
    on(typenames: string, listener: any): Dispatch<T>;
    on(typenames: string, listener: null): Dispatch<T>;
  }

  export function dispatch<T = any>(): Dispatch<T>;
  export function dispatch<T = any>(...types: string[]): Dispatch<T>;
}
