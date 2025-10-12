import React, { useState } from 'react';
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
  // 高级分析结果
  temporal_analysis?: any;
  custom_metrics_analysis?: any;
  multi_dimension_analysis?: any;
  analysis_mode?: string;
}

const App: React.FC = () => {
  const [analysisMode, setAnalysisMode] = useState<'basic' | 'temporal' | 'custom' | 'multi-dimension'>('basic');
  const [customLat, setCustomLat] = useState<number>(39.9042);
  const [customLon, setCustomLon] = useState<number>(116.4074);
  const [customRadius, setCustomRadius] = useState<number>(1000);
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  
  // 自定义指标配置
  const [customMetrics, setCustomMetrics] = useState<string[]>(['土地平整度', '交通便利性', '环境安全性']);
  const [customWeights, setCustomWeights] = useState<{[key: string]: number}>({
    '土地平整度': 0.4,
    '交通便利性': 0.3,
    '环境安全性': 0.3
  });
  
  // 多维度配置
  const [multiDimensions, setMultiDimensions] = useState<{[key: string]: string[]}>({
    '土地利用': ['空地比例', '土地平整度', '可用面积'],
    '环境条件': ['气候适宜性', '自然灾害风险', '环境敏感区'],
    '基础设施': ['交通便利性', '电网接入', '通信覆盖']
  });

  const handleAdvancedAnalyze = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      let requestBody: any = {
        latitude: customLat,
        longitude: customLon,
        radius: customRadius
      };

      switch (analysisMode) {
        case 'temporal':
          endpoint = '/analyze/temporal';
          requestBody.time_points = 3;
          break;
        case 'custom':
          endpoint = '/analyze/custom-metrics';
          requestBody.metrics = customMetrics;
          requestBody.weights = customWeights;
          break;
        case 'multi-dimension':
          endpoint = '/analyze/multi-dimension';
          requestBody.dimensions = multiDimensions;
          break;
        default:
          endpoint = '/analyze/location';
      }

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // 根据分析模式设置不同的数据
      if (analysisMode === 'temporal') {
        setAnalysisData({
          ...data,
          temporal_analysis: data.temporal_analysis,
          analysis_mode: 'temporal'
        });
      } else if (analysisMode === 'custom') {
        setAnalysisData({
          ...data,
          custom_metrics_analysis: data.custom_metrics_analysis,
          analysis_mode: 'custom'
        });
      } else if (analysisMode === 'multi-dimension') {
        setAnalysisData({
          ...data,
          multi_dimension_analysis: data.multi_dimension_analysis,
          analysis_mode: 'multi-dimension'
        });
      } else {
        setAnalysisData(data);
      }
    } catch (error) {
      console.error('高级分析失败:', error);
      alert('分析失败，请检查网络连接或稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <style>{`
        .App {
          text-align: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          color: white;
        }
        
        .mode-selection {
          margin-bottom: 20px;
        }
        
        .mode-buttons {
          display: flex;
          gap: 10px;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .mode-button {
          padding: 10px 20px;
          border: 2px solid rgba(255,255,255,0.3);
          background: rgba(255,255,255,0.1);
          color: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        
        .mode-button:hover {
          background: rgba(255,255,255,0.2);
        }
        
        .mode-button.active {
          background: rgba(0,255,255,0.3);
          border-color: #00ffff;
          box-shadow: 0 0 15px rgba(0,255,255,0.3);
        }
        
        .custom-input-section {
          background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05));
          backdrop-filter: blur(10px);
          padding: 25px;
          border-radius: 15px;
          margin: 20px auto;
          max-width: 1000px;
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
        
        .custom-input, .custom-select {
          padding: 8px 12px;
          border: 1px solid rgba(255,255,255,0.3);
          border-radius: 6px;
          background: rgba(255,255,255,0.1);
          color: white;
          font-size: 14px;
          min-width: 120px;
        }
        
        .custom-input::placeholder {
          color: rgba(255,255,255,0.7);
        }
        
        .analyze-button {
          padding: 12px 24px;
          background: linear-gradient(45deg, #00ffff, #0080ff);
          border: none;
          border-radius: 8px;
          color: white;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(0,255,255,0.3);
        }
        
        .analyze-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(0,255,255,0.4);
        }
        
        .analyze-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }
        
        .config-section {
          margin-top: 20px;
          padding: 20px;
          background: rgba(0,0,0,0.2);
          border-radius: 10px;
          border: 1px solid rgba(255,255,255,0.1);
        }
        
        .metrics-list, .dimensions-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .metric-item, .dimension-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px;
          background: rgba(255,255,255,0.1);
          border-radius: 8px;
        }
        
        .metric-input, .weight-input {
          padding: 6px 10px;
          border: 1px solid rgba(255,255,255,0.3);
          border-radius: 4px;
          background: rgba(255,255,255,0.1);
          color: white;
          font-size: 12px;
        }
        
        .remove-button {
          background: #ff6b6b;
          border: none;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          color: white;
          cursor: pointer;
          font-size: 12px;
        }
        
        .add-metric-button, .add-sub-metric-button {
          padding: 8px 16px;
          background: rgba(0,255,255,0.2);
          border: 1px solid #00ffff;
          border-radius: 6px;
          color: #00ffff;
          cursor: pointer;
          font-size: 12px;
        }
        
        .result-section {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          padding: 20px;
          margin: 20px 0;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .ai-primary {
          background: linear-gradient(135deg, rgba(0, 255, 255, 0.15), rgba(0, 150, 255, 0.15));
          border: 2px solid rgba(0, 255, 255, 0.3);
          box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        }
        
        .ai-primary h3 {
          color: #00ffff;
          text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
      `}</style>

      <header className="App-header">
        <h1>数据中心智能选址与能源优化系统</h1>
        <p>基于真实GEE数据的智能分析平台</p>
        
        {/* 智能分析模式选择 */}
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
          
          {/* 位置输入 */}
          <div className="input-row">
            <div className="input-group">
              <label className="input-label">纬度</label>
              <input
                type="number"
                value={customLat}
                onChange={(e) => setCustomLat(parseFloat(e.target.value))}
                placeholder="39.9042"
                step="0.0001"
                className="custom-input"
              />
            </div>
            <div className="input-group">
              <label className="input-label">经度</label>
              <input
                type="number"
                value={customLon}
                onChange={(e) => setCustomLon(parseFloat(e.target.value))}
                placeholder="116.4074"
                step="0.0001"
                className="custom-input"
              />
            </div>
            <div className="input-group">
              <label className="input-label">分析半径</label>
              <select
                value={customRadius}
                onChange={(e) => setCustomRadius(parseFloat(e.target.value))}
                className="custom-select"
              >
                <option value={500}>500米</option>
                <option value={1000}>1公里</option>
                <option value={2000}>2公里</option>
                <option value={5000}>5公里</option>
              </select>
            </div>
            <button 
              onClick={handleAdvancedAnalyze}
              className="analyze-button"
              disabled={loading}
            >
              {loading ? '分析中...' : '开始分析'}
            </button>
          </div>

          {/* 自定义指标配置 */}
          {analysisMode === 'custom' && (
            <div className="config-section">
              <h3>📊 自定义指标配置</h3>
              <div className="metrics-list">
                {customMetrics.map((metric, index) => (
                  <div key={index} className="metric-item">
                    <input
                      type="text"
                      value={metric}
                      onChange={(e) => {
                        const newMetrics = [...customMetrics];
                        newMetrics[index] = e.target.value;
                        setCustomMetrics(newMetrics);
                      }}
                      className="metric-input"
                      style={{ flex: 1 }}
                    />
                    <input
                      type="number"
                      value={customWeights[metric] * 100}
                      onChange={(e) => {
                        const newWeights = {...customWeights};
                        newWeights[metric] = parseFloat(e.target.value) / 100;
                        setCustomWeights(newWeights);
                      }}
                      min="0"
                      max="100"
                      step="1"
                      className="weight-input"
                      style={{ width: '60px' }}
                    />
                    <span className="weight-label">%</span>
                    <button
                      onClick={() => {
                        const newMetrics = customMetrics.filter((_, i) => i !== index);
                        const newWeights = {...customWeights};
                        delete newWeights[metric];
                        setCustomMetrics(newMetrics);
                        setCustomWeights(newWeights);
                      }}
                      className="remove-button"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    const newMetric = `指标${customMetrics.length + 1}`;
                    setCustomMetrics([...customMetrics, newMetric]);
                    setCustomWeights({...customWeights, [newMetric]: 0.1});
                  }}
                  className="add-metric-button"
                >
                  + 添加指标
                </button>
              </div>
            </div>
          )}

          {/* 多维度配置 */}
          {analysisMode === 'multi-dimension' && (
            <div className="config-section">
              <h3>🎯 多维度分析配置</h3>
              <div className="dimensions-list">
                {Object.entries(multiDimensions).map(([dimension, subMetrics]) => (
                  <div key={dimension} className="dimension-item">
                    <h4 style={{ color: '#00ffff', margin: '0 10px 0 0', minWidth: '100px' }}>{dimension}</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', flex: 1 }}>
                      {subMetrics.map((subMetric, index) => (
                        <div key={index} style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
                          <input
                            type="text"
                            value={subMetric}
                            onChange={(e) => {
                              const newDimensions = {...multiDimensions};
                              newDimensions[dimension][index] = e.target.value;
                              setMultiDimensions(newDimensions);
                            }}
                            className="metric-input"
                            style={{ flex: 1 }}
                          />
                          <button
                            onClick={() => {
                              const newDimensions = {...multiDimensions};
                              newDimensions[dimension] = subMetrics.filter((_, i) => i !== index);
                              setMultiDimensions(newDimensions);
                            }}
                            className="remove-button"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => {
                          const newDimensions = {...multiDimensions};
                          newDimensions[dimension].push(`子指标${subMetrics.length + 1}`);
                          setMultiDimensions(newDimensions);
                        }}
                        className="add-sub-metric-button"
                      >
                        + 添加子指标
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="App-main">
        {analysisData && (
          <div className="results-container">
            <h2>📊 分析结果</h2>
            
            {/* 时间序列分析结果 */}
            {analysisMode === 'temporal' && analysisData.temporal_analysis && (
              <div className="result-section ai-primary">
                <h3>📅 时间序列分析结果</h3>
                <div className="result-content">
                  <div className="ai-analysis">
                    <h4>AI时间序列分析</h4>
                    <div className="ai-content">
                      {analysisData.temporal_analysis.success ? (
                        <div>
                          <p><strong>分析状态:</strong> ✅ 成功</p>
                          <p><strong>分析类型:</strong> {analysisData.temporal_analysis.analysis_type}</p>
                          <p><strong>图片数量:</strong> {analysisData.temporal_analysis.image_count}</p>
                          <p><strong>时间范围:</strong> {analysisData.temporal_analysis.time_range}</p>
                          <div className="ai-insights">
                            <h5>🎯 时间序列洞察:</h5>
                            <p>{analysisData.temporal_analysis.analysis_result || '暂无分析结果'}</p>
                          </div>
                        </div>
                      ) : (
                        <p className="error">时间序列分析失败: {analysisData.temporal_analysis.error}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 自定义指标分析结果 */}
            {analysisMode === 'custom' && analysisData.custom_metrics_analysis && (
              <div className="result-section ai-primary">
                <h3>📊 自定义指标分析结果</h3>
                <div className="result-content">
                  <div className="ai-analysis">
                    <h4>AI自定义指标分析</h4>
                    <div className="ai-content">
                      {analysisData.custom_metrics_analysis.success ? (
                        <div>
                          <p><strong>分析状态:</strong> ✅ 成功</p>
                          <p><strong>分析类型:</strong> {analysisData.custom_metrics_analysis.analysis_type}</p>
                          <p><strong>自定义指标:</strong> {customMetrics.join(', ')}</p>
                          <div className="ai-insights">
                            <h5>🎯 自定义分析洞察:</h5>
                            <p>{analysisData.custom_metrics_analysis.analysis_result || '暂无分析结果'}</p>
                          </div>
                        </div>
                      ) : (
                        <p className="error">自定义指标分析失败: {analysisData.custom_metrics_analysis.error}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 多维度分析结果 */}
            {analysisMode === 'multi-dimension' && analysisData.multi_dimension_analysis && (
              <div className="result-section ai-primary">
                <h3>🎯 多维度分析结果</h3>
                <div className="result-content">
                  <div className="ai-analysis">
                    <h4>AI多维度分析</h4>
                    <div className="ai-content">
                      {analysisData.multi_dimension_analysis.success ? (
                        <div>
                          <p><strong>分析状态:</strong> ✅ 成功</p>
                          <p><strong>分析类型:</strong> {analysisData.multi_dimension_analysis.analysis_type}</p>
                          <p><strong>分析维度:</strong> {Object.keys(multiDimensions).join(', ')}</p>
                          <div className="ai-insights">
                            <h5>🎯 多维度分析洞察:</h5>
                            <p>{analysisData.multi_dimension_analysis.analysis_result || '暂无分析结果'}</p>
                          </div>
                        </div>
                      ) : (
                        <p className="error">多维度分析失败: {analysisData.multi_dimension_analysis.error}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 基础AI分析结果 */}
            {analysisMode === 'basic' && analysisData.ai_multimodal_analysis && (
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
                            <p>{analysisData.ai_multimodal_analysis.analysis_result || '暂无分析结果'}</p>
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
