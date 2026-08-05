import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'money', standalone: true })
export class MoneyPipe implements PipeTransform {
  transform(value: number | null | undefined, signed = false): string {
    if (value === null || value === undefined) return '-';
    const formatted = new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    }).format(Math.abs(value));

    if (signed) {
      return value >= 0 ? `+${formatted}` : `-${formatted}`;
    }
    return value < 0 ? `-${formatted}` : formatted;
  }
}
