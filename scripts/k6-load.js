import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 10,
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95)<1000']
  }
};

export default function () {
  const payload = JSON.stringify({ query: 'Wie hoch ist der aktuelle Durchsatz?' });
  const headers = { 'Content-Type': 'application/json' };
  const res = http.post('http://localhost:8000/chat', payload, { headers });
  check(res, {
    'status is 200': (r) => r.status === 200
  });
  sleep(1);
}
