export function convertLimitlessToMarkdown(input: any): string {
    console.log('convertLimitlessToMarkdown input:', input);

    let lifelogs: any[] | undefined;

    // Try to find the lifelogs array in various common locations
    if (Array.isArray(input)) {
        lifelogs = input;
    } else if (Array.isArray(input?.lifelogs)) {
        lifelogs = input.lifelogs;
    } else if (Array.isArray(input?.data?.lifelogs)) {
        lifelogs = input.data.lifelogs;
    } else if (Array.isArray(input?.data)) {
        // Sometimes data itself is the array
        lifelogs = input.data;
    }

    if (!lifelogs) {
        console.error('Could not find lifelogs array in input');
        return 'No valid data found. Please check console for details.';
    }

    let markdown = '';

    lifelogs.forEach((log: any) => {
        // Add title if available (using the first heading1 or title field)
        const title = log.title || 'Untitled Session';
        markdown += `# ${title}\n\n`;

        // Process contents
        if (log.contents && Array.isArray(log.contents)) {
            log.contents.forEach((item: any) => {
                if (!item.content) return;

                // Determine speaker prefix
                // If speakerName exists and is not empty, use it. 
                // If it's "Unknown", user might want to see it or hide it. 
                // Current request: "話者：contentの内容でまとめるのが理想" -> "Speaker: Content"
                let prefix = '';
                if (item.speakerName) {
                    prefix = `**${item.speakerName}**: `;
                }

                // Simple formatting based on type
                switch (item.type) {
                    case 'heading1':
                        // Already handled title, but if it appears again:
                        markdown += `## ${item.content}\n\n`;
                        break;
                    case 'heading2':
                        markdown += `### ${item.content}\n\n`;
                        break;
                    case 'blockquote':
                        markdown += `- ${prefix}${item.content}\n\n`;
                        break;
                    default:
                        // For other types, also attach speaker if available (though less common for headings)
                        if (prefix && !['heading1', 'heading2'].includes(item.type)) {
                            markdown += `${prefix}${item.content}\n\n`;
                        } else {
                            markdown += `${item.content}\n\n`;
                        }
                }
            });
        }

        markdown += '---\n\n';
    });

    return markdown;
}
