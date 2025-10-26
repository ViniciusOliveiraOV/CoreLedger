// Manual mock for axios to avoid ESM parsing issues in Jest/CI
const axios = {
  get: jest.fn(),
  post: jest.fn(),
  create: () => axios,
};

export default axios;
