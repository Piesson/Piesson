/**
 * Cloudflare Worker: Slack to GitHub Actions Bridge
 *
 * This worker receives messages from Slack and triggers GitHub Actions workflow
 *
 * Required Environment Variables (set in Cloudflare Dashboard):
 * - GITHUB_TOKEN: Personal Access Token with 'repo' and 'workflow' scopes
 * - GITHUB_OWNER: Repository owner (e.g., "Piesson")
 * - GITHUB_REPO: Repository name (e.g., "Piesson")
 * - SLACK_VERIFICATION_TOKEN: (Optional) Slack verification token for security
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Only accept POST requests
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  try {
    // Parse incoming Slack data
    const contentType = request.headers.get('content-type') || ''
    let slackData

    if (contentType.includes('application/x-www-form-urlencoded')) {
      // Slack sends form-encoded data
      const formData = await request.formData()
      slackData = {
        token: formData.get('token'),
        team_id: formData.get('team_id'),
        team_domain: formData.get('team_domain'),
        channel_id: formData.get('channel_id'),
        channel_name: formData.get('channel_name'),
        user_id: formData.get('user_id'),
        user_name: formData.get('user_name'),
        text: formData.get('text'),
        trigger_word: formData.get('trigger_word')
      }
    } else if (contentType.includes('application/json')) {
      // For testing with JSON
      slackData = await request.json()
    } else {
      return new Response('Unsupported content type', { status: 400 })
    }

    // Verify Slack token (optional but recommended)
    if (SLACK_VERIFICATION_TOKEN && slackData.token !== SLACK_VERIFICATION_TOKEN) {
      return new Response('Invalid verification token', { status: 401 })
    }

    // Extract metrics from text
    const text = slackData.text || ''
    const metrics = extractMetrics(text)

    if (!metrics) {
      return new Response(JSON.stringify({
        text: '❌ Invalid format. Please use: `1 0 0 2 0 0 1 1`\n(Talks, IG, TT, HT, Coffee, Blog, Run, Gym)'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    }

    // Trigger GitHub Actions workflow
    const githubResponse = await triggerGitHubWorkflow(metrics)

    if (githubResponse.success) {
      return new Response(JSON.stringify({
        text: `✅ Workflow triggered successfully!\n📊 Metrics: \`${metrics}\`\nCheck GitHub Actions for progress.`
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    } else {
      return new Response(JSON.stringify({
        text: `❌ Failed to trigger workflow: ${githubResponse.error}`
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    }

  } catch (error) {
    console.error('Error:', error)
    return new Response(JSON.stringify({
      text: `❌ Error: ${error.message}`
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Extract metrics from Slack message text
 * Supports formats:
 * - "1 0 0 2 0 0 1 1"
 * - "grind 1 0 0 2 0 0 1 1" (with trigger word)
 * - "1,0,0,2,0,0,1,1" (comma-separated)
 */
function extractMetrics(text) {
  // Remove trigger words
  text = text.replace(/^(grind|update|metrics?)\s+/i, '').trim()

  // Extract numbers
  const numbers = text.match(/\d+/g)

  if (!numbers || numbers.length !== 8) {
    return null
  }

  // Return as space-separated string
  return numbers.join(' ')
}

/**
 * Trigger GitHub Actions workflow via workflow_dispatch
 */
async function triggerGitHubWorkflow(metrics) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/slack_response.yml/dispatches`

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Cloudflare-Worker-Slack-GitHub-Bridge'
      },
      body: JSON.stringify({
        ref: 'main',
        inputs: {
          metrics: metrics
        }
      })
    })

    if (response.status === 204) {
      // 204 No Content = success
      return { success: true }
    } else {
      const errorText = await response.text()
      return {
        success: false,
        error: `GitHub API returned ${response.status}: ${errorText}`
      }
    }
  } catch (error) {
    return {
      success: false,
      error: error.message
    }
  }
}
