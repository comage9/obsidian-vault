# LS Coupang API Endpoints (from /index.js source)

Discovered 2026-06-01 from the minified `/index.js` bundle. All paths are at root `/` on `ls.coupang.com` (no `/api/v1` prefix).

## Core API Groups

### truckOrderApi
| Purpose | Path |
|---------|------|
| Delivery types | `GET /order/deliveryTypes` |
| Order types | `GET /order/orderTypes` |
| Usage types | `GET /order/usageTypes` |
| CPT/Route | `GET /order/route` |
| Create order | `POST /order` |
| Update order | `PUT /order/{orderId}` |
| Templates list | `GET /order/templates` |
| Multi-create (template) | `POST /order/template` |
| Order list | `GET /order` |
| Tracking/sign | `PUT /order/trackingOrSignTruck` |
| Add stops | `POST /order/moreStops` |
| Cancel | `PUT /order/cancel/{requestId}` |
| Back (return) | `PUT /order/back/{requestId}` |
| Validate update | `GET /order/update/validate/{orderId}` |
| Validate creation | `POST /order/creation/validate` |
| Statuses | `GET /order/statuses` |
| Excel download | `GET /order/excelDownload` |
| Single order | `GET /order/{orderId}` |
| Pallet count update | `PUT /order/{orderId}/palletCount` |
| Request excel | `GET /order/requestExcelDownload` |
| File upload | `POST /order/fileUpload` |
| File list | `GET /order/fileList` |
| File download | `GET /order/file/download` |
| File delete | `DELETE /order/file/{truckRequestAttachmentId}/delete` |
| SA pallet count | `PUT /order/{orderId}/saPalletCount` |
| Tote count | `PUT /order/{orderId}/toteCount` |
| Count attributes | `PUT /order/{orderId}/countAttributes` |

### truckOrderTemplateApi
| Purpose | Path |
|---------|------|
| Template list | `GET /truckOrder/templates` |
| Create template | `POST /truckOrder/templates` |
| Update template | `PUT /truckOrder/templates` |
| Delete template | `DELETE /truckOrder/templates/{templateId}` |
| Hub templates | `GET /truckOrder/templates/byHub` |
| Check template | `GET /truckOrder/templates/checkTemplate/{orderDate}` |
| Batch creation | `POST /truckOrder/templates/batch/creation/{orderDate}` |
| Hub template list | `GET /truckOrder/templates/hub` |

### truckOrderTrackingApi
| Purpose | Path |
|---------|------|
| Tracking list | `GET /truckOrderTracking` |
| Update tracking | `PUT /truckOrderTracking/{truckRequestId}` |
| Excel download | `GET /truckOrderTracking/excelDownload` |
| Request excel | `GET /truckOrderTracking/requestExcelDownload` |

### truckRequestApi
| Purpose | Path |
|---------|------|
| Order list | `GET /truckRequest/findRequestsPage` |
| Auto combine | `POST /truckRequest/autoCombine` |
| Submit | `POST /truckRequest/submit/{requestId}` |
| Cancel | `POST /truckRequest/cancel/{requestId}` |
| Back | `POST /truckRequest/back/{requestId}` |
| Update | `PUT /truckRequest/{requestId}` |
| Vendor submit | `POST /truckRequest/vendor/submit/{requestId}` |
| Validate combine | `POST /truckRequest/validateManualCombine` |
| Combine | `POST /truckRequest/combine` |
| Reasons | `GET /truckRequest/reasons` |
| Recall | `POST /truckRequest/recall/{requestId}` |
| Unbind/split | `POST /truckRequest/split/{requestId}` |
| Save truck info | `POST /truckRequest/saveTruckInfo` |
| Detail popup | `GET /truckRequest/getDetail` |
| Excel download | `GET /truckRequest/excelDownload` |
| Excel download detail | `GET /truckRequest/excelDownload/popUp` |
| MRM excel | `GET /truckRequest/excelDownload/milkRun` |
| Arrive time | `GET /truckRequest/arriveTime` |
| Attachment mapping | `GET /truckRequestDetails/attachment/mapping` |
| Batch submit | `POST /truckRequest/batch/submit` |
| Auto combine progress | `GET /truckRequest/getAutoCombineProgress` |
| Split confirm | `POST /truckRequest/unbind/{requestId}` |
| Create combination | `POST /truckRequest/createCombination` |
| Create FC→FC | `POST /truckRequest/createFcToFcRoute` |
| Create mini camp | `POST /truckRequest/createMiniCampRoute` |

### Other APIs (from the source)
- WebSocket: `wss://ls.coupang.com/api/webSocketEndPoint`
- Settlement: `/truckSettlement/...`
- Multi-leg route: `/multiLegRoute/...`
- WorkPlace: `/workPlaces/...`, `/cls/hubs`, `/cls/camps`
- CPF schedule: `/cpf/schedule/...`
- Map dashboard: `/mapDashboard/...`
- ALPR: `/alprMapping`, `/alpr`
- Privacy policy: `/privacyPolicy/...`
- File upload: `/order/fileUpload`
