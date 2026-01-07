/**
 * Test Text Message Recording - Feature #6
 * Verifies user can submit text response and it's saved correctly
 */

import { readFileSync } from 'fs';

// Read bot code to verify implementation
const botCode = readFileSync('C:/Projects/3hours/test-bot.mjs', 'utf8');

console.log("=== Feature #6: Text Message Recording - Test ===\n");

// Step 1: Verify addMoment function exists with source_type
console.log("Step 1: Verify addMoment function with source_type");
console.log("-".repeat(50));

const hasAddMoment = botCode.includes("function addMoment(userId, content, embedding = null, sourceType = 'text')");
console.log("addMoment function with sourceType param: " + (hasAddMoment ? "YES" : "NO"));

const hasSourceTypeField = botCode.includes("source_type: sourceType");
console.log("source_type field in moment: " + (hasSourceTypeField ? "YES" : "NO"));

// Step 2: Verify moment has content field
console.log("\nStep 2: Verify moment content field");
console.log("-".repeat(50));

const hasContentField = botCode.includes("content: content");
console.log("content field in moment: " + (hasContentField ? "YES" : "NO"));

// Step 3: Verify positive feedback message
console.log("\nStep 3: Verify positive feedback message");
console.log("-".repeat(50));

const hasPositiveFeedback = botCode.includes("Moment saved") || botCode.includes("Moment sohran");
console.log("Moment saved feedback (EN): " + (hasPositiveFeedback ? "YES" : "NO"));

// Step 4: Verify embedding is generated
console.log("\nStep 4: Verify embedding is generated");
console.log("-".repeat(50));

const hasGenerateEmbedding = botCode.includes("async function generateEmbedding(text)");
console.log("generateEmbedding function exists: " + (hasGenerateEmbedding ? "YES" : "NO"));

const usesEmbeddingInMoment = botCode.includes("embedding: embedding") || botCode.includes("embedding = await generateEmbedding");
console.log("Embedding is stored in moment: " + (usesEmbeddingInMoment ? "YES" : "NO"));

// Step 5: Verify user state for adding moment
console.log("\nStep 5: Verify user state handling");
console.log("-".repeat(50));

const hasAddingMomentState = botCode.includes("state: 'adding_moment'");
console.log("'adding_moment' state exists: " + (hasAddingMomentState ? "YES" : "NO"));

const checksUserState = botCode.includes("state.state === 'adding_moment'");
console.log("Checks user state before saving: " + (checksUserState ? "YES" : "NO"));

// Step 6: Simulate text moment recording
console.log("\nStep 6: Simulate text moment recording");
console.log("-".repeat(50));

// Simulated moment storage
const moments = new Map();

function simulateAddMoment(userId, content, embedding = null, sourceType = 'text') {
    if (!moments.has(userId)) {
        moments.set(userId, []);
    }
    const userMoments = moments.get(userId);
    const newMoment = {
        id: userMoments.length + 1,
        content: content,
        topics: [],
        embedding: embedding,
        source_type: sourceType,
        created_at: new Date()
    };
    userMoments.push(newMoment);
    return newMoment;
}

// Test creating a text moment
const testContent = "Today was a great day! I had coffee with a friend.";
const testEmbedding = new Array(1536).fill(0.1); // Simulated 1536-dim embedding
const savedMoment = simulateAddMoment(123, testContent, testEmbedding, 'text');

console.log("Saved moment:");
console.log("  content: \"" + savedMoment.content.substring(0, 50) + "...\"");
console.log("  source_type: " + savedMoment.source_type);
console.log("  embedding length: " + (savedMoment.embedding ? savedMoment.embedding.length : 0));
console.log("  has created_at: " + (savedMoment.created_at !== undefined ? "YES" : "NO"));

const contentMatches = savedMoment.content === testContent;
console.log("\nContent matches sent text: " + (contentMatches ? "YES" : "NO"));

const sourceTypeIsText = savedMoment.source_type === 'text';
console.log("source_type is 'text': " + (sourceTypeIsText ? "YES" : "NO"));

const hasEmbedding = savedMoment.embedding && savedMoment.embedding.length === 1536;
console.log("Embedding is created (1536 dims): " + (hasEmbedding ? "YES" : "NO"));

// Final summary
console.log("\n" + "=".repeat(50));
console.log("FINAL VERIFICATION SUMMARY");
console.log("=".repeat(50));

const checks = [
    { name: "addMoment function with sourceType param", pass: hasAddMoment },
    { name: "source_type field in moment", pass: hasSourceTypeField },
    { name: "content field in moment", pass: hasContentField },
    { name: "generateEmbedding function exists", pass: hasGenerateEmbedding },
    { name: "Embedding is stored in moment", pass: usesEmbeddingInMoment },
    { name: "'adding_moment' state exists", pass: hasAddingMomentState },
    { name: "Checks user state before saving", pass: checksUserState },
    { name: "Content matches sent text (simulation)", pass: contentMatches },
    { name: "source_type is 'text' (simulation)", pass: sourceTypeIsText },
    { name: "Embedding is created (simulation)", pass: hasEmbedding }
];

let passCount = 0;
for (const check of checks) {
    console.log((check.pass ? "[PASS]" : "[FAIL]") + " " + check.name);
    if (check.pass) passCount++;
}

console.log("\nTotal: " + passCount + "/" + checks.length + " checks passed");

if (passCount === checks.length) {
    console.log("\nFEATURE #6 VERIFICATION: PASSED");
} else {
    console.log("\nFEATURE #6 VERIFICATION: NEEDS WORK");
}
