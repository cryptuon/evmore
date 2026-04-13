import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    author: z.string().default('EVMORE Team'),
    tags: z.array(z.string()),
    image: z.string().optional(),
    imageAlt: z.string().optional(),
    draft: z.boolean().default(false),
    seoKeywords: z.array(z.string()).optional(),
    comparison: z.boolean().default(false),
    relatedSlugs: z.array(z.string()).optional(),
  }),
});

export const collections = { blog };
