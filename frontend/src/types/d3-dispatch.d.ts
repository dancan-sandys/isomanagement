// Custom type declarations to fix d3-dispatch TypeScript issues
declare module '@types/d3-dispatch' {
  export interface Dispatch<T = any> {
    on(typenames: string): (listener: any) => Dispatch<T>;
    on(typenames: string, listener: any): Dispatch<T>;
    on(typenames: string, listener: null): Dispatch<T>;
  }

  export function dispatch<T = any>(): Dispatch<T>;
  export function dispatch<T = any>(...types: string[]): Dispatch<T>;
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
