export function evaluate(a, b, operation) {
  return  eval(`(${a}) ${operation} (${b})`);
}