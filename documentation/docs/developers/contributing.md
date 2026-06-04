# Contributing to EVMORE

EVMORE is an open-source project and contributions are welcome. This guide covers how to get involved.

---

## Ways to Contribute

### Code

- **Smart contracts** -- Optimize gas usage, add features for future stages
- **Mining software** -- Improve the miner, add GPU kernels, optimize algorithms
- **Frontend** -- Enhance the Vue 3 dApp (wallet, mining, bridge, dashboard views)
- **Tests** -- Expand test coverage, add edge case tests, fuzz testing

### Non-Code

- **Documentation** -- Fix errors, improve clarity, add examples
- **Security** -- Report vulnerabilities, review code, participate in audits
- **Community** -- Help others on Discord, write tutorials, create content

---

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/evmore-contracts
cd evmore-contracts
uv sync && npm install
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Follow existing code patterns and conventions
- Add tests for new functionality
- Update documentation if your change affects user-facing behavior

### 4. Test

```bash
# Run the full test suite
uv run ape test

# Compile to check for Vyper errors
uv run ape compile
```

### 5. Submit a Pull Request

- Write a clear PR description explaining what and why
- Reference any related issues
- Ensure tests pass

---

## Code Standards

### Vyper Contracts

- Use Vyper 0.4.0 syntax
- Follow checks-effects-interactions pattern
- Add reentrancy guards to state-changing functions
- Use descriptive variable names
- Keep functions focused and short

### Python Scripts

- Python 3.12+
- Use type hints
- Follow existing patterns in `scripts/`

### Frontend (Vue 3 + TypeScript)

- TypeScript strict mode
- Composition API with `<script setup>`
- Tailwind CSS for styling
- Pinia for state management

---

## Security

If you discover a security vulnerability, **do not** open a public issue. Instead:

1. Contact the team privately via Discord DM to a moderator
2. Provide details of the vulnerability
3. Allow time for a fix before public disclosure

---

## Community

- **GitHub Issues** -- Bug reports and feature requests
- **Discord** -- Discussion and real-time help
- **Twitter** -- Announcements and updates

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
