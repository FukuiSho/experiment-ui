
import type { NextConfig } from 'next';

// Check if 'turbopack' is a valid top-level property
const config1: NextConfig = {
    turbopack: {
        root: '.'
    }
};

// Check if 'turbo' is valid in 'experimental'
const config2: NextConfig = {
    experimental: {
        turbo: {
            root: '.'
        }
    }
};
