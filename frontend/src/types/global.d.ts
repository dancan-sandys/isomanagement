// Global type declarations to fix third-party library issues

declare module 'd3-dispatch' {
  export interface Dispatch<This = any, EventMap = any> {
    on(typenames: string): this;
    on(typenames: string, listener: null): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void, capture?: boolean): this;
  }

  export function dispatch<This = any, EventMap = any>(): Dispatch<This, EventMap>;
}

// Override problematic d3-dispatch types
declare module '@types/d3-dispatch' {
  export interface Dispatch<This = any, EventMap = any> {
    on(typenames: string): this;
    on(typenames: string, listener: null): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void): this;
    on(typenames: string, listener: (this: This, ...args: any[]) => void, capture?: boolean): this;
  }

  export function dispatch<This = any, EventMap = any>(): Dispatch<This, EventMap>;
}

// Global React types
declare global {
  namespace React {
    interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
      type: T;
      props: P;
      key: Key | null;
    }
  }
}

export {};
