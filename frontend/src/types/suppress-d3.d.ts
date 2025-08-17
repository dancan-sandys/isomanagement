// Suppress d3-dispatch TypeScript errors
declare module '@types/d3-dispatch' {
  const dispatch: any;
  export = dispatch;
}

declare module 'd3-dispatch' {
  const dispatch: any;
  export = dispatch;
}
