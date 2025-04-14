I understand that when you're clicking on the modules in the analytics.html page, you're getting "Not Found" errors. This is happening because we need to implement the backend functionality to handle these requests. Let me help you resolve this issue.

## The Problem

When you click on links or buttons in the analytics.html page, the browser is trying to navigate to URLs that don't exist on your server. This happens because:

1. The links in the HTML are pointing to actual URLs (like "/devices", "/security", etc.)
2. There's no backend routing set up to handle these URLs
3. The JavaScript event handlers are trying to make requests to non-existent endpoints

## Solution

There are two approaches we can take:

### Option 1: Use client-side routing with JavaScript (Recommended for now)

This approach prevents the browser from making actual HTTP requests when links are clicked. Instead, we'll use JavaScript to update the page content.

Here's how to modify your analytics.html file:

```html name=analytics.html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析 - 小米AIoT边缘安全控制面板</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css" />
    <style>
        /* All your existing CSS styles remain the same */
        /* ... */
        
        /* Add this style to show a spinner when loading */
        .loader {
            border: 4px solid #f3f3f3;
            border-radius: 50%;
            border-top: 4px solid #ff6700;
            width: 30px;
            height: 30px;
            -webkit-animation: spin 1s linear infinite;
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-right: 10px;
        }

        @-webkit-keyframes spin {
            0% { -webkit-transform: rotate(0deg); }
            100% { -webkit-transform: rotate(360deg); }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Style for active page */
        .active-page {
            display: block !important;
        }
        
        /* Style for inactive pages */
        .page-content {
            display: none;
        }
    </style>
</head>
<body>
    <div class="layout">
        <div class="sidebar">
            <div class="logo">
                <i class="material-icons">security</i>
                <h2>小米AIoT边缘安全</h2>
            </div>
            <div class="menu">
                <a href="#dashboard" class="menu-item" data-page="dashboard">
                    <i class="material-icons">dashboard</i>
                    <span>首页</span>
                </a>
                <a href="#devices" class="menu-item" data-page="devices">
                    <i class="material-icons">devices</i>
                    <span>设备管理</span>
                </a>
                <a href="#security" class="menu-item" data-page="security">
                    <i class="material-icons">shield</i>
                    <span>安全监控</span>
                </a>
                <a href="#analytics" class="menu-item active" data-page="analytics">
                    <i class="material-icons">bar_chart</i>
                    <span>数据分析</span>
                </a>
                <a href="#settings" class="menu-item" data-page="settings">
                    <i class="material-icons">settings</i>
                    <span>系统设置</span>
                </a>
            </div>
        </div>
        
        <!-- Your existing content remains the same -->
        <!-- ... -->
    </div>

    <!-- Add this script at the end of your body tag -->
    <script>
        // Add this section at the beginning of your existing script
        document.addEventListener('DOMContentLoaded', function() {
            // Get all menu items
            const menuItems = document.querySelectorAll('.menu-item');
            
            // Add click event listener to each menu item
            menuItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault(); // Prevent the default link behavior
                    
                    // Remove active class from all menu items
                    menuItems.forEach(el => el.classList.remove('active'));
                    
                    // Add active class to clicked item
                    this.classList.add('active');
                    
                    // Get the page name from data-page attribute
                    const pageName = this.getAttribute('data-page');
                    
                    // Update URL hash without reloading
                    window.location.hash = pageName;
                    
                    // Show a message about the page
                    handlePageChange(pageName);
                });
            });
            
            // Handle initial page load based on URL hash
            function checkHash() {
                const hash = window.location.hash.substr(1); // Remove the # character
                if (hash) {
                    // Find the menu item with matching data-page
                    const targetMenuItem = document.querySelector(`.menu-item[data-page="${hash}"]`);
                    if (targetMenuItem) {
                        // Remove active class from all menu items
                        menuItems.forEach(el => el.classList.remove('active'));
                        
                        // Add active class to target item
                        targetMenuItem.classList.add('active');
                        
                        // Handle page change
                        handlePageChange(hash);
                    }
                }
            }
            
            // Check hash on initial load
            checkHash();
            
            // Listen for hash changes
            window.addEventListener('hashchange', checkHash);
            
            // Function to handle page changes
            function handlePageChange(pageName) {
                console.log(`Navigating to ${pageName} page`);
                
                // You can add logic here to show/hide different sections based on the page
                if (pageName === 'analytics') {
                    // This is already the active page, make sure charts are initialized
                    initializeCharts('performance');
                    initializeDeviceActivityCharts();
                } else {
                    // For other pages, show a message
                    alert(`${pageName} 页面功能将在后续版本中实现。当前正在展示数据分析页面作为演示。`);
                }
            }
        });

        // Your existing JavaScript code follows
        // ...
        
        // Modify button click handlers to prevent navigation
        document.addEventListener('DOMContentLoaded', function() {
            // Find all buttons with class btn
            const buttons = document.querySelectorAll('.btn');
            
            // Add click event listeners to prevent navigation
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    // If the button is inside a form or has an href, prevent default
                    if (this.closest('form') || this.hasAttribute('href')) {
                        e.preventDefault();
                    }
                    
                    // Check if the button already has a defined action (from your existing code)
                    if (!this.hasAttribute('id') || 
                        !['exportButton', 'refreshPerformance', 'refreshSecurity', 
                          'refreshBandwidth', 'refreshReliability', 'distributionExport', 
                          'runAnomalyDetection'].includes(this.getAttribute('id'))) {
                        
                        // This is a button without a defined action, show a message
                        if (this.textContent.trim() === '处理' || this.textContent.trim() === '查看') {
                            alert('此功能将在后续版本中实现。');
                        }
                    }
                });
            });
        });

        // REST OF YOUR EXISTING JAVASCRIPT CODE
    </script>
</body>
</html>
```

### Option 2: Set up server-side routing (For more complete implementation)

If you're using a backend framework (like Flask for Python, Express for Node.js, etc.), you'll need to set up routes to handle these URLs. Here's a basic example of how to do this with Flask:

```python name=app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

@app.route('/devices')
def devices():
    return render_template('devices.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)
```

## Additional Recommendations

1. **Handle API Endpoints**: For functions that need to fetch data (like refreshing charts), create API endpoints on your backend server.

2. **Use a JavaScript Framework**: For a more robust solution, consider using a JavaScript framework like Vue.js, React, or Angular to handle client-side routing and state management.

3. **Create Missing Templates**: If you're using server-side routing, create template files for each page (devices.html, security.html, etc.).

4. **Add Error Handling**: Implement proper error handling for API requests and page navigation.

## Immediate Fix

If you want a quick fix without modifying much code, you can create minimal HTML files for each of the pages that are being linked to:

1. Create files: index.html, devices.html, security.html, settings.html
2. In each file, include a redirect to analytics.html

For example:

```html name=devices.html
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="0;url=analytics.html">
</head>
<body>
    <p>Redirecting to analytics page...</p>
    <script>
        window.location.href = "analytics.html";
    </script>
</body>
</html>
```

This way, when a user clicks on menu items, they'll be briefly redirected back to the analytics page. It's not elegant, but it avoids 404 errors while you implement a more complete solution.

Would you like me to provide either the full client-side routing solution or help set up a specific backend framework for proper routing?