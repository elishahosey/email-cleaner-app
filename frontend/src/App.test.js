import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Intro from './Intro/introduction';

test('renders the Email Cleaner landing page', () => {
  render(<MemoryRouter><Intro /></MemoryRouter>);
  expect(screen.getByRole('heading', { name: /inbox triage console/i })).toBeInTheDocument();
});
