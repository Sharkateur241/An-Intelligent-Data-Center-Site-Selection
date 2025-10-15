import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

interface AnalysisData {
  location: { latitude: number; longitude: number };
  land_analysis: any;
  energy_assessment: any;
  decision_recommendation: any;
  heat_utilization: any;
  geographic_environment: any;
  power_supply_analysis: any;
  energy_storage_analysis: any;
  promethee_mcgp_analysis: any;
  // AI分析结果
  ai_multimodal_analysis?: any;
  ai_energy_analysis?: any;
  ai_power_supply_analysis?: any;
  ai_energy_storage_analysis?: any;
  ai_decision_analysis?: any;
  // 新增分析结果
  regional_analysis?: any;
  heat_utilization_analysis?: any;
}

const App: React.FC = () => {
  const [analysisMode, setAnalysisMode] = useState<'basic' | 'temporal' | 'custom' | 'multi-dimension'>('basic');
  const [customMetrics, setCustomMetrics] = useState<string[]>(['土地平整度', '交通便利性', '环境安全性']);
  const [customWeights, setCustomWeights] = useState<{[key: string]: number}>({
    '土地平整度': 0.4,
    '交通便利性': 0.3,
    '环境安全性': 0.3
  });
  const [multiDimensions, setMultiDimensions] = useState<{[key: string]: string[]}>({
    '土地利用': ['空地比例', '土地平整度', '可用面积'],
    '环境条件': ['气候适宜性', '自然灾害风险', '环境敏感区'],
    '基础设施': ['交通便利性', '电网接入', '通信覆盖']
  });

  // 添加内联样式
  const styles = `
    .custom-input-section {
      background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
      backdrop-filter: blur(10px);
      padding: 25px;
      border-radius: 15px;
      margin: 20px auto;
      max-width: 800px;
      border: 1px solid rgba(255,255,255,0.2);
      box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .input-row {
      display: flex;
      gap: 15px;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 15px;
    }
    
    .input-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 5px;
    }
    
    .input-label {
      color: #fff;
      font-size: 14px;
      font-weight: 500;
    }
    
    .input-field {
      padding: 8px 12px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.3);
      background: rgba(255,255,255,0.1);
      color: #fff;
      font-size: 14px;
      width: 120px;
      text-align: center;
    }
    
    .input-field::placeholder {
      color: rgba(255,255,255,0.6);
    }
    
    .input-field:focus {
      outline: none;
      border-color: #61dafb;
      box-shadow: 0 0 0 2px rgba(97, 218, 251, 0.2);
    }
    
    .analyze-button {
      padding: 10px 20px;
      background: linear-gradient(45deg, #61dafb, #21a0c4);
      color: #000;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: bold;
      font-size: 14px;
      transition: all 0.3s ease;
      box-shadow: 0 4px 15px rgba(97, 218, 251, 0.3);
    }
    
    .analyze-button:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(97, 218, 251, 0.4);
    }
    
    .analyze-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    
    .area-info {
      font-size: 13px;
      color: rgba(255,255,255,0.8);
      text-align: center;
      margin-top: 10px;
      padding: 8px;
      background: rgba(255,255,255,0.1);
      border-radius: 6px;
    }
    
    .result-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    
    .result-section {
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .satellite-section {
      grid-column: 1 / -1;
      order: -1;
    }
    
    .satellite-image {
      margin: 10px 0;
      position: relative;
      overflow: hidden;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .satellite-image img {
      transition: transform 0.3s ease;
    }
    
    .satellite-image:hover img {
      transform: scale(1.02);
    }
    
    .image-caption {
      font-size: 12px;
      color: #666;
      text-align: center;
      margin-top: 5px;
    }
    
    .result-content p {
      margin: 8px 0;
      padding: 5px 0;
      border-bottom: 1px solid #eee;
    }
    
    .result-content p:last-child {
      border-bottom: none;
    }
  `;
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<{lat: number, lng: number} | null>(null);
  const [customLat, setCustomLat] = useState<string>('');
  const [customLng, setCustomLng] = useState<string>('');
  const [customRadius, setCustomRadius] = useState<number>(1000);

  const cities = [
    { name: '北京', lat: 39.9042, lng: 116.4074 },
    { name: '上海', lat: 31.2304, lng: 121.4737 },
    { name: '深圳', lat: 22.5431, lng: 114.0579 },
    { name: '杭州', lat: 30.2741, lng: 120.1551 },
    { name: '中卫', lat: 37.5149, lng: 105.1967 },
    { name: '贵阳', lat: 26.6470, lng: 106.6302 },
    { name: '广州', lat: 23.1291, lng: 113.2644 },
    { name: '兰州', lat: 36.0611, lng: 103.8343 }
  ];

  const handleAnalyze = async (lat: number, lng: number, radius: number = 1000) => {
    setLoading(true);
    try {
      // 先调用主要分析API
      const basicResponse = await fetch('http://localhost:8000/analyze/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: lat, longitude: lng, radius: radius })
      });

      if (basicResponse.ok) {
        const basicData = await basicResponse.json();
        
        // 尝试调用其他API（不阻塞主要功能）
        Promise.allSettled([
          fetch('http://localhost:8000/analyze/regional', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lng, radius: radius })
          }),
          fetch('http://localhost:8000/analyze/heat-utilization', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude: lat, longitude: lng, radius: radius })
          })
        ]).then(([regionalResult, heatResult]) => {
          if (regionalResult.status === 'fulfilled' && regionalResult.value.ok) {
            regionalResult.value.json().then(data => {
              basicData.regional_analysis = data;
              setAnalysisData({...basicData}); // 触发重新渲染
            });
          }
          if (heatResult.status === 'fulfilled' && heatResult.value.ok) {
            heatResult.value.json().then(data => {
              basicData.heat_utilization_analysis = data;
              setAnalysisData({...basicData}); // 触发重新渲染
            });
          }
        });
        
        setAnalysisData(basicData);
        alert('分析完成！');
      } else {
        const errorText = await basicResponse.text();
        console.error('API Error:', basicResponse.status, errorText);
        throw new Error(`分析失败 (${basicResponse.status}): ${errorText}`);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert(`分析失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <style>{styles}</style>
      <header className="App-header">
        <h1>数据中心智能选址与能源优化系统</h1>
        <p>基于真实GEE数据的智能分析平台</p>
        
        {/* 自定义坐标输入区域 */}
        <div className="custom-input-section">
          <h3 style={{ margin: '0 0 20px 0', color: '#fff', textAlign: 'center', fontSize: '18px' }}>
            🎯 智能分析模式
          </h3>
          
          {/* 分析模式选择 */}
          <div className="mode-selection">
            <h4 style={{ color: '#fff', marginBottom: '15px' }}>选择分析模式：</h4>
            <div className="mode-buttons">
              <button 
                className={`mode-button ${analysisMode === 'basic' ? 'active' : ''}`}
                onClick={() => setAnalysisMode('basic')}
              >
                🤖 基础AI分析
              </button>
              <button 
                className={`mode-button ${analysisMode === 'temporal' ? 'active' : ''}`}
                onClick={() => setAnalysisMode('temporal')}
              >
                📅 时间序列分析
              </button>
              <button 
                className={`mode-button ${analysisMode === 'custom' ? 'active' : ''}`}
                onClick={() => setAnalysisMode('custom')}
              >
                📊 自定义指标
              </button>
              <button 
                className={`mode-button ${analysisMode === 'multi-dimension' ? 'active' : ''}`}
                onClick={() => setAnalysisMode('multi-dimension')}
              >
                🎯 多维度分析
              </button>
            </div>
          </div>
          
          <div className="input-row">
            <div className="input-group">
              <label className="input-label">纬度</label>
              <input 
                type="number" 
                step="0.0001"
                placeholder="39.9042"
                value={customLat}
                onChange={(e) => setCustomLat(e.target.value)}
                className="input-field"
              />
            </div>
            
            <div className="input-group">
              <label className="input-label">经度</label>
              <input 
                type="number" 
                step="0.0001"
                placeholder="116.4074"
                value={customLng}
                onChange={(e) => setCustomLng(e.target.value)}
                className="input-field"
              />
            </div>
            
            <div className="input-group">
              <label className="input-label">分析半径</label>
              <select 
                value={customRadius}
                onChange={(e) => setCustomRadius(Number(e.target.value))}
                className="input-field"
                style={{ width: '140px' }}
              >
                <option value={500}>500米</option>
                <option value={1000}>1000米</option>
                <option value={2000}>2000米</option>
                <option value={5000}>5000米</option>
                <option value={10000}>10000米</option>
              </select>
            </div>
            
            <button 
              onClick={() => {
                if (customLat && customLng) {
                  const lat = parseFloat(customLat);
                  const lng = parseFloat(customLng);
                  if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
                    handleAnalyze(lat, lng, customRadius);
                  } else {
                    alert('请输入有效的坐标范围：纬度(-90到90)，经度(-180到180)');
                  }
                } else {
                  alert('请输入纬度和经度');
                }
              }}
              disabled={loading}
              className="analyze-button"
            >
              {loading ? '分析中...' : '🚀 开始分析'}
            </button>
          </div>
          
          <div className="area-info">
            💡 分析面积: {Math.round(Math.PI * (customRadius/1000) ** 2 * 100) / 100} 平方公里
          </div>
        </div>
      </header>

      <main className="App-main">
        <div className="location-section">
          <h2>位置选择</h2>
          <div className="city-buttons">
            {cities.map(city => (
              <button
                key={city.name}
                onClick={() => {
                  setSelectedLocation({ lat: city.lat, lng: city.lng });
                  handleAnalyze(city.lat, city.lng);
                }}
                disabled={loading}
                className="city-button"
              >
                {city.name}
              </button>
            ))}
          </div>
          
          {selectedLocation && (
            <div className="selected-location">
              <p>已选择位置: {selectedLocation.lat.toFixed(4)}, {selectedLocation.lng.toFixed(4)}</p>
            </div>
          )}
        </div>

        {loading && (
          <div className="loading">
            <p>正在分析中，请稍候...</p>
          </div>
        )}

        {analysisData && (
          <div className="analysis-results">
            <h2>分析结果</h2>
            
            <div className="result-grid">
              {/* 卫星图像 - 放在最前面 */}
              <div className="result-section satellite-section">
                <h3>🛰️ 卫星图像</h3>
                <div className="satellite-image">
                  <img 
                    src={analysisData.geographic_environment?.satellite_image_url} 
                    alt="卫星图像" 
                    style={{
                      width: '100%', 
                      height: '500px', 
                      objectFit: 'cover', 
                      borderRadius: '8px',
                      imageRendering: 'high-quality' as any
                    }}
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = `https://via.placeholder.com/400x600/4CAF50/FFFFFF?text=位置: ${analysisData.location?.latitude?.toFixed(2)}, ${analysisData.location?.longitude?.toFixed(2)}`;
                    }}
                  />
                </div>
                <p className="image-caption">
                  基于GEE的高分辨率卫星图像<br/>
                  Landsat 8/9数据 | 覆盖半径: {analysisData.geographic_environment?.satellite_image_metadata?.coverage_radius || `${customRadius/1000}公里`} | 实时更新
                </p>
              </div>


              {/* 土地利用分析 - 显示总面积 */}
              {analysisData.land_analysis && (
                <div className="result-section">
                  <h3>🏗️ 土地利用与环境分析</h3>
                  <div className="result-content">
                    <p><strong>总面积:</strong> {analysisData.land_analysis.land_use_analysis?.total_area?.toLocaleString() || '计算中...'} 平方米</p>
                    <p><strong>分析日期:</strong> {analysisData.land_analysis.analysis_date ? new Date(analysisData.land_analysis.analysis_date).toLocaleString() : '未知'}</p>
                    {analysisData.land_analysis.land_use_analysis?.land_cover_distribution && (
                      <div>
                        <p><strong>土地利用分布:</strong></p>
                        <ul>
                          {Object.entries(analysisData.land_analysis.land_use_analysis.land_cover_distribution).map(([key, value]) => (
                            <li key={key}>{key}: {((value as number) * 100).toFixed(1)}%</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* 区域特色分析 */}
                    {analysisData.regional_analysis && analysisData.regional_analysis.success && (
                      <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                        <h4 style={{ color: '#1890ff', marginBottom: '10px' }}>🌍 区域特色分析</h4>
                        <p><strong>区域类型:</strong> {analysisData.regional_analysis.region_type}</p>
                        <p><strong>分析时间:</strong> {analysisData.regional_analysis.timestamp}</p>
                        {analysisData.regional_analysis.recommendations && (
                          <div>
                            <p><strong>区域建议:</strong></p>
                            <div className="markdown-content" style={{ 
                              background: '#f5f5f5', 
                              padding: '10px', 
                              borderRadius: '6px', 
                              marginTop: '8px',
                              fontSize: '13px'
                            }}>
                              <ReactMarkdown>{analysisData.regional_analysis.recommendations.join('\n')}</ReactMarkdown>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* 余热利用分析 */}
                    {analysisData.heat_utilization_analysis && analysisData.heat_utilization_analysis.success && (
                      <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #eee' }}>
                        <h4 style={{ color: '#1890ff', marginBottom: '10px' }}>🔥 余热利用分析</h4>
                        <p><strong>区域类型:</strong> {analysisData.heat_utilization_analysis.region_type}</p>
                        <p><strong>分析时间:</strong> {analysisData.heat_utilization_analysis.timestamp}</p>
                        {analysisData.heat_utilization_analysis.implementation_recommendations && (
                          <div>
                            <p><strong>余热利用建议:</strong></p>
                            <div className="markdown-content" style={{ 
                              background: '#f5f5f5', 
                              padding: '10px', 
                              borderRadius: '6px', 
                              marginTop: '8px',
                              fontSize: '13px'
                            }}>
                              <ReactMarkdown>{analysisData.heat_utilization_analysis.implementation_recommendations.join('\n')}</ReactMarkdown>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}


        {/* AI多模态分析 - 主要分析结果 */}
        {analysisData.ai_multimodal_analysis && (
          <div className="result-section ai-primary">
            <h3>🤖 AI智能分析（主要结果）</h3>
            <div className="result-content">
              <div className="ai-analysis">
                <h4>AI土地利用与环境分析</h4>
                <div className="ai-content">
                  {analysisData.ai_multimodal_analysis.success ? (
                    <div>
                      <p><strong>分析状态:</strong> ✅ 成功</p>
                      <p><strong>分析时间:</strong> {analysisData.ai_multimodal_analysis.timestamp}</p>
                      <div className="ai-insights">
                        <h5>🎯 AI智能洞察:</h5>
                        <div className="markdown-content" style={{ 
                          background: '#f5f5f5', 
                          padding: '15px', 
                          borderRadius: '8px', 
                          marginTop: '10px'
                        }}>
                          <ReactMarkdown>{analysisData.ai_multimodal_analysis.analysis || analysisData.ai_multimodal_analysis.analysis_result || '暂无分析结果'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="error">AI分析失败: {analysisData.ai_multimodal_analysis.error}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI能源分析 - 主要能源评估 */}
        {analysisData.ai_energy_analysis && (
          <div className="result-section ai-primary">
            <h3>⚡ AI能源资源评估（主要结果）</h3>
            <div className="result-content">
              <div className="ai-analysis">
                <h4>AI能源潜力分析</h4>
                <div className="ai-content">
                  {analysisData.ai_energy_analysis.success ? (
                    <div>
                      <p><strong>分析状态:</strong> ✅ 成功</p>
                      <p><strong>分析时间:</strong> {analysisData.ai_energy_analysis.timestamp}</p>
                      <div className="ai-insights">
                        <h5>⚡ 能源评估:</h5>
                        <div className="markdown-content" style={{
                          background: '#f5f5f5', 
                          padding: '15px', 
                          borderRadius: '8px', 
                          marginTop: '10px'
                        }}>
                          <ReactMarkdown>{analysisData.ai_energy_analysis.analysis || analysisData.ai_energy_analysis.analysis_result || '暂无分析结果'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="error">AI能源分析失败: {analysisData.ai_energy_analysis.error}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI供电分析 - 主要供电方案 */}
        {analysisData.ai_power_supply_analysis && (
          <div className="result-section ai-primary">
            <h3>🔌 AI供电方案（主要结果）</h3>
            <div className="result-content">
              <div className="ai-analysis">
                <h4>AI供电策略评估</h4>
                <div className="ai-content">
                  {analysisData.ai_power_supply_analysis.success ? (
                    <div>
                      <p><strong>分析状态:</strong> ✅ 成功</p>
                      <p><strong>分析时间:</strong> {analysisData.ai_power_supply_analysis.timestamp}</p>
                      <div className="ai-insights">
                        <h5>🔌 供电建议:</h5>
                        <div className="markdown-content" style={{
                          background: '#f5f5f5', 
                          padding: '15px', 
                          borderRadius: '8px', 
                          marginTop: '10px'
                        }}>
                          <ReactMarkdown>{analysisData.ai_power_supply_analysis.analysis || analysisData.ai_power_supply_analysis.analysis_result || '暂无分析结果'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="error">AI供电分析失败: {analysisData.ai_power_supply_analysis.error}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI储能分析 - 主要储能方案 */}
        {analysisData.ai_energy_storage_analysis && (
          <div className="result-section ai-primary">
            <h3>🔋 AI储能方案（主要结果）</h3>
            <div className="result-content">
              <div className="ai-analysis">
                <h4>AI储能策略评估</h4>
                <div className="ai-content">
                  {analysisData.ai_energy_storage_analysis.success ? (
                    <div>
                      <p><strong>分析状态:</strong> ✅ 成功</p>
                      <p><strong>分析时间:</strong> {analysisData.ai_energy_storage_analysis.timestamp}</p>
                      <div className="ai-insights">
                        <h5>🔋 储能建议:</h5>
                        <div className="markdown-content" style={{
                          background: '#f5f5f5', 
                          padding: '15px', 
                          borderRadius: '8px', 
                          marginTop: '10px'
                        }}>
                          <ReactMarkdown>{analysisData.ai_energy_storage_analysis.analysis || analysisData.ai_energy_storage_analysis.analysis_result || '暂无分析结果'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="error">AI储能分析失败: {analysisData.ai_energy_storage_analysis.error}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI决策分析 - 主要决策建议 */}
        {analysisData.ai_decision_analysis && (
          <div className="result-section ai-primary">
            <h3>🎯 AI综合决策（主要结果）</h3>
            <div className="result-content">
              <div className="ai-analysis">
                <h4>AI智能决策建议</h4>
                <div className="ai-content">
                  {analysisData.ai_decision_analysis.success ? (
                    <div>
                      <p><strong>分析状态:</strong> ✅ 成功</p>
                      <p><strong>分析时间:</strong> {analysisData.ai_decision_analysis.timestamp}</p>
                      <div className="ai-insights">
                        <h5>🎯 决策建议:</h5>
                        <div className="markdown-content" style={{ 
                          background: '#f5f5f5', 
                          padding: '15px', 
                          borderRadius: '8px', 
                          marginTop: '10px'
                        }}>
                          <ReactMarkdown>{analysisData.ai_decision_analysis.analysis || analysisData.ai_decision_analysis.analysis_result || '暂无分析结果'}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="error">AI决策分析失败: {analysisData.ai_decision_analysis.error}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}


            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2024 数据中心智能选址与能源优化系统 - 使用真实GEE数据</p>
      </footer>
    </div>
  );
};

export default App;
