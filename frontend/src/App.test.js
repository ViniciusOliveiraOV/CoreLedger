// Ensure Jest uses the manual mock before any imports
jest.mock('axios');

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from './App';

// Minimal WebSocket stub for the test environment
beforeAll(() => {
  global.WebSocket = class {
    constructor() {
      // simulate open on next tick
      setTimeout(() => {
        if (this.onopen) this.onopen();
      }, 0);
    }
    send() {}
    close() {}
  };
});

test('renders dashboard header', async () => {
  axios.get.mockResolvedValue({
    data: {
      kpis: {
        timestamp: new Date().toISOString(),
        total_balance: 0,
        total_accounts: 0,
        today_transactions: 0,
        month_transactions: 0,
      },
      charts: {
        transaction_types: [],
        accounts: [],
        recent_transactions: []
      }
    }
  });

  render(<App />);

  await waitFor(() => expect(screen.getByText(/CoreLedger Dashboard/i)).toBeInTheDocument());
});
