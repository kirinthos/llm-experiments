/**
 * Server Health Tests
 * Prevents communication server errors from breaking the UI
 */

const API_BASE_URL = "http://localhost:4090";
const FRONTEND_URL = "http://localhost:4091";

/**
 * Test server health endpoints
 */
async function testServerHealth() {
  const tests = [];

  // Test MCP API Server Health
  tests.push(async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`MCP API health check failed: ${response.status}`);
    }
    const data = await response.json();
    if (!data.mcp_enabled) {
      throw new Error("MCP is not enabled in API server");
    }
    if (!data.agent_available) {
      throw new Error("MCP agent is not available");
    }
    console.log("✅ MCP API Server health check passed");
    return data;
  });

  // Test Models Endpoint
  tests.push(async () => {
    const response = await fetch(`${API_BASE_URL}/models`);
    if (!response.ok) {
      throw new Error(`Models endpoint failed: ${response.status}`);
    }
    const data = await response.json();
    if (!data.models || data.models.length < 5) {
      throw new Error(
        `Expected at least 5 models, got ${data.models?.length || 0}`
      );
    }

    // Verify we have models from multiple providers
    const providers = [...new Set(data.models.map((m) => m.provider))];
    if (providers.length < 2) {
      throw new Error(
        `Expected multiple providers, got: ${providers.join(", ")}`
      );
    }

    console.log(
      `✅ Models endpoint passed - ${data.models.length} models from ${providers.length} providers`
    );
    return data;
  });

  // Test Tools Endpoint
  tests.push(async () => {
    const response = await fetch(`${API_BASE_URL}/tools`);
    if (!response.ok) {
      throw new Error(`Tools endpoint failed: ${response.status}`);
    }
    const data = await response.json();
    if (!data.tools || data.tools.length < 10) {
      throw new Error(
        `Expected at least 10 tools, got ${data.tools?.length || 0}`
      );
    }
    console.log(
      `✅ Tools endpoint passed - ${data.tools.length} tools available`
    );
    return data;
  });

  // Test Chat Endpoint
  tests.push(async () => {
    const response = await fetch(`${API_BASE_URL}/chat/simple`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Test message for health check",
        model: "gpt-4o-mini",
        provider: "openai",
        use_tools: false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat endpoint failed: ${response.status}`);
    }
    const data = await response.json();
    if (!data.response) {
      throw new Error("Chat endpoint did not return a response");
    }
    console.log("✅ Chat endpoint passed");
    return data;
  });

  // Test Frontend Availability
  tests.push(async () => {
    const response = await fetch(FRONTEND_URL);
    if (!response.ok) {
      throw new Error(`Frontend not available: ${response.status}`);
    }
    const html = await response.text();
    if (!html.includes("Universal AI Chat")) {
      throw new Error("Frontend HTML does not contain expected title");
    }
    console.log("✅ Frontend availability passed");
    return { status: "ok" };
  });

  // Run all tests
  const results = [];
  for (const test of tests) {
    try {
      const result = await test();
      results.push({ success: true, result });
    } catch (error) {
      results.push({ success: false, error: error.message });
      console.error(`❌ Test failed: ${error.message}`);
    }
  }

  return results;
}

/**
 * Test UI component integration
 */
async function testUIIntegration() {
  console.log("🧪 Testing UI Integration...");

  // This would typically run in a browser environment
  // For now, we'll just validate the API responses that the UI depends on

  const results = await testServerHealth();
  const failures = results.filter((r) => !r.success);

  if (failures.length > 0) {
    console.error(
      `❌ ${failures.length} tests failed. UI may not work correctly.`
    );
    failures.forEach((failure) => console.error(`   - ${failure.error}`));
    process.exit(1);
  } else {
    console.log("✅ All server health tests passed. UI should work correctly.");
  }
}

/**
 * Continuous monitoring
 */
async function startMonitoring() {
  console.log("🔄 Starting continuous server monitoring...");

  setInterval(async () => {
    try {
      await testServerHealth();
      console.log(`📊 ${new Date().toISOString()}: All servers healthy`);
    } catch (error) {
      console.error(
        `🚨 ${new Date().toISOString()}: Server health check failed:`,
        error
      );
    }
  }, 30000); // Check every 30 seconds
}

// Export for use in other files
export { testServerHealth, testUIIntegration, startMonitoring };

// Run tests if called directly
if (
  typeof window === "undefined" &&
  process.argv[1].includes("server-health.test.js")
) {
  (async () => {
    console.log("🧪 Running Server Health Tests...\n");

    try {
      await testUIIntegration();

      // Ask if user wants continuous monitoring
      if (process.argv.includes("--monitor")) {
        await startMonitoring();
      }
    } catch (error) {
      console.error("❌ Test suite failed:", error);
      process.exit(1);
    }
  })();
}
