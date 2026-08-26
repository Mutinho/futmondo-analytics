import { NativeDateAdapter } from '@angular/material/core';

export const ES_DATE_FORMATS = {
  parse: { dateInput: 'dd/MM/yyyy' },
  display: {
    dateInput: { day: '2-digit', month: '2-digit', year: 'numeric' } as Intl.DateTimeFormatOptions,
    monthYearLabel: { year: 'numeric', month: 'short' } as Intl.DateTimeFormatOptions,
    dateA11yLabel: { year: 'numeric', month: 'long', day: 'numeric' } as Intl.DateTimeFormatOptions,
    monthYearA11yLabel: { year: 'numeric', month: 'long' } as Intl.DateTimeFormatOptions,
  },
};

export class SpanishDateAdapter extends NativeDateAdapter {
  override getFirstDayOfWeek(): number {
    return 1; // Monday
  }

  override format(date: Date, displayFormat: Object): string {
    if (displayFormat === ES_DATE_FORMATS.display.dateInput) {
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    }
    return super.format(date, displayFormat);
  }
}
