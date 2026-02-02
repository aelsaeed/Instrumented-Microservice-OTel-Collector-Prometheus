import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const payload = JSON.stringify({ name: `item-${__VU}-${__ITER}`, description: 'sample' });
  const headers = { 'Content-Type': 'application/json' };
  const createRes = http.post('http://localhost:8000/items', payload, { headers });
  check(createRes, { 'created': (r) => r.status === 200 });

  const id = createRes.json('id');
  const getRes = http.get(`http://localhost:8000/items/${id}`);
  check(getRes, { 'fetched': (r) => r.status === 200 });
  sleep(1);
}
